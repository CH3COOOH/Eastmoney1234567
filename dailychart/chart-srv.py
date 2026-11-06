import argparse
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import logging
import time

from pathlib import Path
from datetime import datetime, timedelta


# ==================================================
# 1. 基础配置
# ==================================================

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# 本地缓存保留天数。缓存越长，MACD EMA预热越充分。
CACHE_KEEP_DAYS = 120

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "charts"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "minute_cache"

for directory in (OUTPUT_DIR, LOG_DIR, DATA_DIR, CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

IMAGE_DPI = 180
IMAGE_WIDTH = 16
IMAGE_HEIGHT = 10

# K线实体宽度（分钟）。1分钟K线建议 0.6～0.75。
CANDLE_WIDTH_MINUTES = 0.65


# ==================================================
# 2. 日志配置
# ==================================================

log_file = LOG_DIR / "generate_chart.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ==================================================
# 3. Matplotlib配置
# ==================================================

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Arial"
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"


# ==================================================
# 4. 数据清洗
# ==================================================

def clean_data(df):
    required = ["时间", "开盘", "最高", "最低", "收盘"]

    for col in required:
        if col not in df.columns:
            raise RuntimeError(f"行情数据缺少必要字段：{col}")

    result = df.copy()
    result["时间"] = pd.to_datetime(result["时间"], errors="coerce")

    for col in ["开盘", "最高", "最低", "收盘"]:
        result[col] = pd.to_numeric(result[col], errors="coerce")

    if "成交量" in result.columns:
        result["成交量"] = pd.to_numeric(
            result["成交量"], errors="coerce"
        ).fillna(0)
    else:
        result["成交量"] = 0

    result = result.dropna(
        subset=["时间", "开盘", "最高", "最低", "收盘"]
    )
    result = result.sort_values("时间")
    result = result.drop_duplicates(subset=["时间"], keep="last")
    result = result.reset_index(drop=True)

    if result.empty:
        raise RuntimeError("清洗后没有有效行情数据")

    return result[["时间", "开盘", "最高", "最低", "收盘", "成交量"]]


# ==================================================
# 5. 获取当天一分钟行情
# ==================================================

def get_market_data(symbol, security_type):
    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = "2222-01-01 00:00:00"

    logger.info("开始获取%s（%s）一分钟行情...", symbol, security_type)

    market_data_api = (
        ak.stock_zh_a_hist_min_em
        if security_type == "stock"
        else ak.index_zh_a_hist_min_em
    )
    minute_raw = market_data_api(
        symbol=symbol,
        period="1",
        start_date=start_date,
        end_date=end_date
    )

    if minute_raw is None or minute_raw.empty:
        raise RuntimeError("一分钟行情数据为空")

    minute_df = clean_data(minute_raw)
    logger.info("一分钟行情获取成功，共 %d 条", len(minute_df))
    return minute_df


# ==================================================
# 6. 本地缓存：逐日积累一分钟行情
# ==================================================

def update_minute_cache(today_df, cache_file):
    """
    将接口返回的数据合并进本地CSV。
    同一时间戳重复时，以本次接口返回的数据为准，
    因此盘中重复运行也会更新当前分钟的数据。
    """
    if cache_file.exists():
        try:
            old_df = clean_data(pd.read_csv(cache_file))
            merged = pd.concat([old_df, today_df], ignore_index=True)
        except Exception:
            logger.exception("读取本地分钟缓存失败，将使用本次行情重建缓存")
            merged = today_df.copy()
    else:
        merged = today_df.copy()

    merged = clean_data(merged)

    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=CACHE_KEEP_DAYS)
    merged = merged[merged["时间"] >= cutoff].copy()
    merged.to_csv(cache_file, index=False, encoding="utf-8-sig")

    logger.info(
        "一分钟缓存已更新：%s，共 %d 条，覆盖 %s 至 %s",
        cache_file,
        len(merged),
        merged["时间"].min(),
        merged["时间"].max()
    )
    return merged


# ==================================================
# 7. 获取昨收
# ==================================================

def get_previous_close(trade_date, cache_df, symbol, security_type):
    """
    优先从东方财富日线接口取得前一交易日收盘价。
    若日线接口暂时不可用，则退回本地缓存中的最近一个
    更早交易日的最后一条分钟收盘价。
    """
    try:
        start = (trade_date - timedelta(days=15)).strftime("%Y%m%d")
        end = trade_date.strftime("%Y%m%d")

        daily_data_api = (
            ak.stock_zh_a_hist
            if security_type == "stock"
            else ak.index_zh_a_hist
        )
        daily = daily_data_api(
            symbol=symbol,
            period="daily",
            start_date=start,
            end_date=end
        )

        if daily is not None and not daily.empty:
            date_col = "日期" if "日期" in daily.columns else "date"
            close_col = "收盘" if "收盘" in daily.columns else "close"

            daily[date_col] = pd.to_datetime(daily[date_col], errors="coerce")
            daily[close_col] = pd.to_numeric(daily[close_col], errors="coerce")

            previous = daily[
                (daily[date_col].dt.date < trade_date)
                & daily[close_col].notna()
            ].sort_values(date_col)

            if not previous.empty:
                value = float(previous.iloc[-1][close_col])
                logger.info("昨收来自日线接口：%.3f", value)
                return value
    except Exception:
        logger.exception("获取日线昨收失败，尝试使用本地缓存")

    previous_days = cache_df[
        cache_df["时间"].dt.date < trade_date
    ].copy()

    if not previous_days.empty:
        previous_day = previous_days["时间"].dt.date.max()
        previous_rows = previous_days[
            previous_days["时间"].dt.date == previous_day
        ]
        value = float(previous_rows.iloc[-1]["收盘"])
        logger.warning(
            "昨收使用本地缓存估算（最近缓存日期 %s）：%.3f",
            previous_day, value
        )
        return value

    logger.warning("没有可用的昨收数据，将使用当日第一根K线开盘价作为参考")
    return None


# ==================================================
# 8. 计算一分钟MACD
# ==================================================

def calculate_macd(df):
    """
    使用缓存中的跨交易日一分钟收盘价连续计算EMA，
    计算完成后绘图时只截取当天数据。
    缓存首次建立时，MACD只能从已有数据开始预热。
    """
    result = df.copy().sort_values("时间").reset_index(drop=True)
    close = result["收盘"]

    ema_fast = close.ewm(
        span=MACD_FAST, adjust=False, min_periods=1
    ).mean()

    ema_slow = close.ewm(
        span=MACD_SLOW, adjust=False, min_periods=1
    ).mean()

    result["DIF"] = ema_fast - ema_slow
    result["DEA"] = result["DIF"].ewm(
        span=MACD_SIGNAL, adjust=False, min_periods=1
    ).mean()
    result["MACD"] = (result["DIF"] - result["DEA"]) * 2

    return result


# ==================================================
# 9. 绘制图表
# ==================================================

def draw_chart(
    minute_today,
    macd_today,
    trade_date,
    previous_close,
    symbol,
    name,
    security_type,
):
    if len(minute_today) < 2:
        raise RuntimeError("当天一分钟行情不足，暂时无法绘图")

    minute_today = minute_today.sort_values("时间").copy()
    macd_today = macd_today.sort_values("时间").copy()

    latest_row = minute_today.iloc[-1]
    latest_price = float(latest_row["收盘"])
    first_time = minute_today["时间"].min()
    last_time = minute_today["时间"].max()

    if previous_close is not None and previous_close != 0:
        change_points = latest_price - previous_close
        change_percent = change_points / previous_close * 100
        change_label = (
            f"最新价 {latest_price:.2f}    "
            f"涨跌 {change_points:+.2f} 点 ({change_percent:+.2f}%)    "
            f"昨收 {previous_close:.2f}"
        )
        change_color = "red" if change_points >= 0 else "green"
        reference_price = previous_close
        reference_label = f"昨收 {previous_close:.2f}"
    else:
        first_open = float(minute_today.iloc[0]["开盘"])
        change_points = latest_price - first_open
        change_percent = (
            change_points / first_open * 100 if first_open else 0
        )
        change_label = (
            f"最新价 {latest_price:.2f}    "
            f"相对首根开盘 {change_points:+.2f} 点 ({change_percent:+.2f}%)"
        )
        change_color = "red" if change_points >= 0 else "green"
        reference_price = first_open
        reference_label = f"首根开盘 {first_open:.2f}"

    logger.info(
        "开始绘图：%s，一分钟K线 %d 条，数据截止 %s",
        trade_date, len(minute_today), last_time
    )

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(IMAGE_WIDTH, IMAGE_HEIGHT),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1.5], "hspace": 0.08}
    )

    # ---------------- 上图：一分钟K线 ----------------

    ax1.set_title(
        f"{name}（{symbol}）一分钟K线 + 一分钟MACD\n"
        f"{trade_date}    数据截止：{last_time:%H:%M}",
        fontsize=17,
        pad=15
    )

    candle_width = CANDLE_WIDTH_MINUTES / (24 * 60)

    for row in minute_today.itertuples(index=False):
        x = mdates.date2num(row.时间)
        open_price = float(row.开盘)
        high_price = float(row.最高)
        low_price = float(row.最低)
        close_price = float(row.收盘)

        # A股习惯：上涨红色，下跌绿色
        color = "red" if close_price >= open_price else "green"

        ax1.vlines(
            x, low_price, high_price,
            color=color, linewidth=0.75, zorder=2
        )

        bottom = min(open_price, close_price)
        height = abs(close_price - open_price)

        if height < 0.001:
            ax1.hlines(
                open_price,
                x - candle_width / 2,
                x + candle_width / 2,
                color=color,
                linewidth=1.0,
                zorder=3
            )
        else:
            body = Rectangle(
                (x - candle_width / 2, bottom),
                candle_width,
                height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.5,
                alpha=0.85,
                zorder=3
            )
            ax1.add_patch(body)

    ax1.axhline(
        reference_price,
        color="gray",
        linestyle="--",
        linewidth=1.6,
        alpha=0.7,
        label=reference_label,
        zorder=1
    )

    price_range = max(
        reference_price - minute_today["最低"].min(),
        minute_today["最高"].max() - reference_price,
        abs(reference_price) * 0.001,
        0.01,
    )
    centered_range = price_range * 1.05
    ax1.set_ylim(
        reference_price - centered_range,
        reference_price + centered_range,
    )

    ax1.axhline(
        latest_price,
        color="#2878B5",
        linestyle=":",
        linewidth=0.8,
        alpha=0.8
    )

    ax1.text(
        0.99, 0.96,
        change_label,
        transform=ax1.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        color=change_color,
        weight="bold"
    )

    ax1.set_ylabel("价格 / 点位")
    ax1.grid(True, alpha=0.25)
    ax1.legend(loc="upper left", fontsize=9)

    # ---------------- 下图：一分钟MACD ----------------

    macd_width = 0.65 / (24 * 60)
    macd_colors = [
        "#E74C3C" if value >= 0 else "#27AE60"
        for value in macd_today["MACD"]
    ]

    ax2.bar(
        macd_today["时间"],
        macd_today["MACD"],
        width=macd_width,
        color=macd_colors,
        alpha=0.8,
        label="MACD柱"
    )

    ax2.plot(
        macd_today["时间"], macd_today["DIF"],
        color="#2878B5", linewidth=1.2, label="DIF"
    )
    ax2.plot(
        macd_today["时间"], macd_today["DEA"],
        color="#E6A23C", linewidth=1.2, label="DEA"
    )

    ax2.axhline(0, color="gray", linewidth=0.8)
    ax2.set_ylabel("MACD")
    ax2.set_xlabel("交易时间")
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="upper left", fontsize=9, ncol=3)

    latest_macd = macd_today.iloc[-1]
    macd_info = (
        f"DIF {latest_macd['DIF']:.3f}    "
        f"DEA {latest_macd['DEA']:.3f}    "
        f"MACD {latest_macd['MACD']:.3f}"
    )

    ax2.text(
        0.99, 0.95, macd_info,
        transform=ax2.transAxes,
        ha="right", va="top",
        fontsize=9, color="#333333"
    )

    # 时间轴：午休自然留白，符合真实钟表时间
    ax2.xaxis.set_major_locator(
        mdates.MinuteLocator(byminute=[0, 30])
    )
    ax2.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M")
    )

    ax2.set_xlim(
        first_time - timedelta(minutes=2),
        last_time + timedelta(minutes=2)
    )

    fig.tight_layout()

    filename = f"{symbol}-{security_type}-latest.jpg"
    output_path = OUTPUT_DIR / filename

    fig.savefig(
        output_path,
        format="jpg",
        dpi=IMAGE_DPI,
        bbox_inches="tight",
        facecolor="white"
    )
    plt.close(fig)

    logger.info("图片生成成功：%s", output_path)
    return output_path


# ==================================================
# 10. 主程序
# ==================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="获取A股或指数的一分钟行情并生成K线与MACD图表"
    )
    parser.add_argument("symbol", nargs="?", help="六位证券代码，例如 600000")
    parser.add_argument("name", nargs="?", help="证券名称，例如 浦发银行")
    parser.add_argument(
        "--security-type",
        choices=("stock", "index"),
        help="证券类型：stock 或 index（提供代码时默认 stock）",
    )
    args = parser.parse_args()
    if args.symbol is None and args.name is None:
        args.symbol = "000300"
        args.name = "沪深300"
        args.security_type = args.security_type or "index"
    elif args.symbol is None or args.name is None:
        parser.error("symbol 和 name 必须同时提供")
    else:
        args.security_type = args.security_type or "stock"

    if len(args.symbol) != 6 or not args.symbol.isdigit():
        parser.error("symbol 必须是六位数字代码")
    return args


def main():
    args = parse_args()
    cache_file = CACHE_DIR / f"{args.symbol}_{args.security_type}_1min.csv"
    logger.info("=" * 60)
    logger.info("%s（%s）一分钟K线 + 一分钟MACD图表生成任务启动",
                args.name, args.symbol)

    try:
        minute_today = None

        # 获取行情，失败时最多重试3次
        for attempt in range(3):
            try:
                minute_today = get_market_data(args.symbol, args.security_type)
                break
            except Exception as exc:
                logger.warning(
                    "获取行情失败，第 %d 次：%s", attempt + 1, exc
                )
                if attempt == 2:
                    raise
                time.sleep(5)

        trade_date = minute_today["时间"].dt.date.max()
        minute_today = minute_today[
            minute_today["时间"].dt.date == trade_date
        ].copy()

        if minute_today.empty:
            raise RuntimeError("没有找到当天一分钟行情")

        # 先保存当前数据，再从跨日缓存计算MACD
        cache_df = update_minute_cache(minute_today, cache_file)

        # 获取昨收，用于计算当日涨跌
        previous_close = get_previous_close(
            trade_date, cache_df, args.symbol, args.security_type
        )

        # 用缓存中的所有历史分钟数据预热EMA
        macd_all = calculate_macd(cache_df)

        # 绘图只使用当天数据
        macd_today = macd_all[
            macd_all["时间"].dt.date == trade_date
        ].copy()

        if macd_today.empty:
            raise RuntimeError("当天MACD数据为空")

        output_path = draw_chart(
            minute_today,
            macd_today,
            trade_date,
            previous_close,
            args.symbol,
            args.name,
            args.security_type,
        )

        logger.info("任务完成")
        logger.info("输出文件：%s", output_path)

    except Exception:
        logger.exception("行情图表生成失败")
        raise

    finally:
        logger.info("任务结束")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
