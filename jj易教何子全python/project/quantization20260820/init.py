# -*- coding: utf-8 -*-
"""
实时股票行情查看器

功能：
    1. 输入股票代码（如 600519 / 000001 / 300750，或 sh600519）
    2. 交易时段内每隔几秒实时刷新显示股价
    3. 非交易时段（周末、节假日、开盘前、收盘后、停牌）显示"暂无交易"

数据来源：腾讯免费行情接口 qt.gtimg.cn
"""

import datetime
import re
import time

import requests

# ---------------- 配置 ----------------
QUOTE_URL = "https://qt.gtimg.cn/q={symbol}"
REFRESH_INTERVAL = 3   # 刷新间隔（秒）
TIMEOUT = 5            # 请求超时（秒）

# A股交易时段：上午 9:30-11:30，下午 13:00-15:00
TRADING_SESSIONS = (
    (datetime.time(9, 30), datetime.time(11, 30)),
    (datetime.time(13, 0), datetime.time(15, 0)),
)


def normalize_code(raw: str) -> str:
    """把用户输入规范为接口所需的市场前缀代码，如 600519 -> sh600519"""
    code = raw.strip().lower()
    if re.fullmatch(r"(sh|sz|bj)\d{6}", code):
        return code
    if re.fullmatch(r"\d{6}", code):
        if code.startswith("6"):
            return "sh" + code                     # 沪市主板
        if code.startswith(("0", "3")):
            return "sz" + code                     # 深市主板 / 创业板
        if code.startswith(("4", "8", "9")):
            return "bj" + code                     # 北交所
    raise ValueError("请输入 6 位数字股票代码（如 600519），或带市场前缀（如 sh600519）")


def is_trading_time(now: datetime.datetime | None = None) -> bool:
    """判断是否处于 A 股交易时段（周一~周五 + 交易时段；节假日由行情日期兜底判断）"""
    now = now or datetime.datetime.now()
    if now.weekday() >= 5:                         # 周六、周日休市
        return False
    t = now.time()
    return any(start <= t <= end for start, end in TRADING_SESSIONS)


def fetch_quote(symbol: str) -> dict | None:
    """请求腾讯行情接口并解析，返回行情字典；失败返回 None"""
    try:
        resp = requests.get(
            QUOTE_URL.format(symbol=symbol),
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.encoding = "gbk"                      # 接口返回 GBK 编码
    except requests.RequestException:
        return None

    m = re.search(r'"([^"]+)"', resp.text)
    if not m:
        return None
    f = m.group(1).split("~")
    if len(f) < 38 or not f[3]:
        return None
    return {
        "name": f[1],           # 名称
        "code": f[2],           # 代码
        "price": f[3],          # 当前价
        "prev_close": f[4],     # 昨收
        "open": f[5],           # 今开
        "quote_time": f[30],    # 行情时间 yyyymmddHHMMSS
        "change": f[31],        # 涨跌额
        "change_pct": f[32],    # 涨跌幅 %
        "high": f[33],          # 最高
        "low": f[34],           # 最低
        "volume": f[36],        # 成交量（手）
        "amount": f[37],        # 成交额（万元）
    }


def build_line(now: datetime.datetime, q: dict) -> str:
    """交易中：拼接单行实时行情文本"""
    try:
        change = float(q["change"])
    except (TypeError, ValueError):
        change = 0.0
    arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
    return (
        f'{now:%H:%M:%S} {q["name"]}({q["code"]}) '
        f'现价 {q["price"]} {arrow}{q["change"]} ({q["change_pct"]}%) | '
        f'今开 {q["open"]} 最高 {q["high"]} 最低 {q["low"]} 昨收 {q["prev_close"]}'
    )


def monitor(symbol: str, max_refreshes: int | None = None) -> None:
    """主循环：交易中实时显示股价，否则显示"暂无交易"及原因"""
    print(f"开始监控 {symbol}，每 {REFRESH_INTERVAL} 秒刷新一次，按 Ctrl+C 退出\n")
    n = 0
    try:
        while max_refreshes is None or n < max_refreshes:
            now = datetime.datetime.now()
            q = fetch_quote(symbol)

            if not is_trading_time(now):
                msg = "暂无交易（当前不在交易时段）"
            elif q is None:
                msg = "暂无交易（行情获取失败，请检查网络）"
            elif q["quote_time"][:8] != now.strftime("%Y%m%d"):
                msg = "暂无交易（今日休市，无交易数据）"
            elif float(q["open"] or 0) == 0:
                msg = "暂无交易（今日无成交，可能停牌）"
            else:
                msg = None

            if msg:
                print(f"\r{now:%Y-%m-%d %H:%M:%S}  {msg}", end="", flush=True)
            else:
                print("\r\033[K" + build_line(now, q), end="", flush=True)

            n += 1
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        pass
    print("\n\n已退出行情监控。")


def main() -> None:
    print("=" * 50)
    print("            A 股实时行情查看器")
    print("=" * 50)

    # 循环获取输入，直到合法或退出
    while True:
        raw = input("请输入股票代码（如 600519，输入 q 退出）：").strip()
        if not raw:
            continue
        if raw.lower() in ("q", "quit", "exit"):
            print("再见！")
            return
        try:
            symbol = normalize_code(raw)
        except ValueError as e:
            print(f"[输入错误] {e}")
            continue
        break

    # 先请求一次，确认代码有效并显示股票名称
    q = fetch_quote(symbol)
    if q is None or not q["name"]:
        print("[错误] 未查询到该股票，请确认代码是否正确。")
        return
    print(f'已找到：{q["name"]}（{q["code"]}）\n')

    monitor(symbol)


if __name__ == "__main__":
    main()