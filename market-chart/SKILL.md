---
name: market-chart
description: "使用项目中的 chart-srv.py 获取A股或指数的最新行情并生成一分钟K线与MACD图表。用户要求获取股票行情、指数行情或生成行情图时使用。"
argument-hint: "[股票代码和名称] [代理地址] [图片路径]"
user-invocable: true
---

# 行情图表生成

使用项目现有的 `market-chart\chart-srv.py` 获取最新分钟行情并生成K线/MACD图。不要重新实现行情获取或绘图逻辑。

## 操作步骤

1. 用户指定股票时，将六位代码和名称作为位置参数传入。未指定标的时不传位置参数，脚本默认获取沪深300指数（`000300`、`沪深300`）。
2. 选择标的类型：
   - A股默认使用 `stock`，无需额外指定类型。
   - 用户指定指数时，传入 `--security-type index`。
3. 用户提供代理时，通过 `--proxy` 传入。支持 HTTP、HTTPS、SOCKS5 和 SOCKS5H URL；未提供代理时省略此选项，使用直连。
4. 用户指定图片保存位置时，通过 `--filename` 传入。绝对路径直接使用；相对路径放在脚本的 `charts` 目录下。未指定时，默认文件名为 `<代码>-<类型>-latest.jpg`。
5. 在工作区中使用 Python 直接运行脚本。不要预先检查脚本、依赖或环境，直接运行所需命令。
6. 成功时报告生成的图片路径。失败时根据实际错误信息说明可能原因；命令失败时绝不能声称图表已生成。

## 命令示例

生成默认指数图：

```powershell
python market-chart\chart-srv.py
```

生成股票图：

```powershell
python market-chart\chart-srv.py 600000 "浦发银行"
```

指定指数、SOCKS5代理和自定义绝对保存路径：

```powershell
python market-chart\chart-srv.py 000300 "沪深300" --security-type index --proxy socks5://127.0.0.1:1080 --filename "D:\charts\hs300.jpg"
```

## 说明

- 脚本通过 AkShare 获取分钟行情，按标的维护本地分钟缓存，并基于缓存计算 MACD。
- 根据命令的实际输出报告代理和网络错误。不要擅自换用其他代理重试，也不要在没有证据时声称代理可用。
- 除非用户另行要求修改代码，否则不要修改行情图表程序。
