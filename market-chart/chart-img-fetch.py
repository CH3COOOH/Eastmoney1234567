import argparse
from pathlib import Path

# python .\chart-fetch.py --capture-selector ".board-wrap" --wait-for-selector "#canvasMask"

BASE_DIR = Path(__file__).resolve().parent
CHARTS_DIR = BASE_DIR / "charts"
CHART_URL = "https://q.10jqka.com.cn/zs/detail/code/1B0300/"


def parse_args():
    parser = argparse.ArgumentParser(
        description="打开行情网页并保存截图。"
    )
    parser.add_argument(
        "--url",
        default=CHART_URL,
        help=f"行情网页地址（默认：{CHART_URL}）",
    )
    parser.add_argument(
        "--name",
        default="hs300",
        help="股票或指数名称，用于默认截图文件名（默认：hs300）",
    )
    parser.add_argument(
        "--output",
        help="自定义PNG截图路径；相对路径保存到 market-chart/charts",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="显示浏览器窗口（默认无头模式）",
    )
    parser.add_argument(
        "--wait-for-selector",
        help="等待该页面元素可见后截图，最多等待30秒；默认页面加载后等待5秒",
    )
    capture_group = parser.add_mutually_exclusive_group()
    capture_group.add_argument(
        "--capture-selector",
        help="只截取匹配的页面元素，例如 '#chart' 或 '.chart-container'",
    )
    capture_group.add_argument(
        "--full-page",
        action="store_true",
        help="截取整个页面，而不是当前视图",
    )
    return parser.parse_args()


def get_output_path(output, name):
    if output:
        path = Path(output).expanduser()
        if not path.is_absolute():
            path = CHARTS_DIR / path
        if not path.suffix:
            path = path.with_suffix(".png")
        elif path.suffix.lower() != ".png":
            raise SystemExit("--output 路径必须使用 .png 扩展名")
    else:
        path = CHARTS_DIR / f"{name}-latest.png"

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def main():
    args = parse_args()
    output_path = get_output_path(args.output, args.name)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "缺少 Playwright，请运行：pip install playwright，"
            "然后运行：python -m playwright install firefox"
        ) from exc

    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=not args.show_browser)
        try:
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
            if args.wait_for_selector:
                page.locator(args.wait_for_selector).wait_for(
                    state="visible",
                    timeout=30000,
                )
            else:
                page.wait_for_timeout(5000)

            if args.capture_selector:
                capture_element = page.locator(args.capture_selector)
                capture_element.wait_for(state="visible", timeout=30000)
                capture_element.screenshot(path=str(output_path), type="png")
            else:
                page.screenshot(
                    path=str(output_path),
                    full_page=args.full_page,
                    type="png",
                )
        finally:
            if browser.is_connected():
                browser.close()

    print(f"截图已保存：{output_path}")


if __name__ == "__main__":
    main()