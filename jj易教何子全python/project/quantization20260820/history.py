# -*- coding: utf-8 -*-
"""
历史股价查询器

功能：
    1. 输入股票代码（如 600519 / 000001 / 300750，或 sh600519）
    2. 输入开始时间、结束时间（格式：2025-01-02 00:01:02）
    3. 输入时间间隔（单位：秒）
    4. 输出从开始时间到结束时间、每隔该间隔的股价列表，结构如：
       [
           {'时间': '2025-01-02 00:00:00', 'price': '45'},
           {'时间': '2025-01-02 00:00:01', 'price': '46'},
       ]

数据来源：腾讯免费行情接口
    - 日K线（覆盖长区间历史，价格精确到天）
    - 1分钟K线（仅最近若干交易日，价格精确到分钟）

说明：
    免费接口没有秒级历史数据。对每个时间点，采用"前向填充"：
    取不晚于该时间点的最近一条行情的价格（如凌晨取前一交易日收盘价）。
"""

import bisect
import datetime
import json
import re

import requests

# ---------------- 配置 ----------------
# 日K线（前复权），param=代码,周期,开始日期,结束日期,数量,复权方式
DAILY_URL = (
    "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    "?param={symbol},day,{start},{end},640,qfq"
)
# 1分钟K线，param=代码,周期,起始位置,数量
MINUTE_URL = (
    "https://web.ifzq.gtimg.cn/appstock/app/kline/mkline"
    "?param={symbol},m1,,320"
)
TIMEOUT = 10                 # 请求超时（秒）
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_POINTS = 5000            # 最多输出的数据点数，防止间隔过小刷屏


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


def parse_time(text: str) -> datetime.datetime:
    """解析时间字符串，如 2025-01-02 00:01:02"""
    try:
        return datetime.datetime.strptime(text.strip(), TIME_FORMAT)
    except ValueError:
        raise ValueError("时间格式应为 2025-01-02 00:01:02")


def _get_json(url: str) -> dict | None:
    """请求接口并解析 JSON，失败返回 None"""
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        return resp.json()
    except (requests.RequestException, json.JSONDecodeError):
        return None


def fetch_daily_klines(symbol: str, start: datetime.datetime,
                       end: datetime.datetime) -> list:
    """获取日K线（前复权），返回 [(时间, 收盘价), ...]

    开始日期往前多取 15 天，用于给查询区间第一天凌晨的时间点
    提供"前一交易日收盘价"做前向填充。收盘价标记在当天 15:00。
    """
    fetch_start = (start - datetime.timedelta(days=15)).date()
    data = _get_json(DAILY_URL.format(symbol=symbol, start=fetch_start, end=end.date()))
    if not data:
        return []
    node = data.get("data", {}).get(symbol, {})
    rows = node.get("qfqday") or node.get("day") or []
    result = []
    for row in rows:
        # row: [日期, 开盘, 收盘, 最高, 最低, 成交量]
        close_time = datetime.datetime.strptime(row[0], "%Y-%m-%d").replace(hour=15)
        result.append((close_time, row[2]))
    return result


def fetch_minute_klines(symbol: str) -> list:
    """获取最近约 320 根 1 分钟K线，返回 [(时间, 收盘价), ...]"""
    data = _get_json(MINUTE_URL.format(symbol=symbol))
    if not data:
        return []
    rows = data.get("data", {}).get(symbol, {}).get("m1", [])
    result = []
    for row in rows:
        # row: [时间yyyymmddHHMM, 开盘, 收盘, 最高, 最低, 成交量]
        t = datetime.datetime.strptime(row[0], "%Y%m%d%H%M")
        result.append((t, row[2]))
    return result


def build_price_series(symbol: str, start: datetime.datetime,
                       end: datetime.datetime) -> list:
    """合并日K线与分钟K线，得到按时间升序的价格序列 [(时间, 价格), ...]

    同一时刻以分钟线为准（精度更高）。
    """
    series = fetch_daily_klines(symbol, start, end)
    series += fetch_minute_klines(symbol)
    merged = {t: price for t, price in series}
    return sorted(merged.items())


def query_prices(symbol: str, start: datetime.datetime, end: datetime.datetime,
                 interval: int) -> list:
    """生成 [开始时间, 结束时间] 内每隔 interval 秒的时间点，返回价格列表"""
    series = build_price_series(symbol, start, end)
    if not series:
        return []

    times = [t for t, _ in series]
    prices = [p for _, p in series]

    result = []
    t = start
    while t <= end:
        # 前向填充：找不晚于 t 的最近一条数据；t 早于全部数据时用最早一条
        i = bisect.bisect_right(times, t) - 1
        price = prices[i] if i >= 0 else prices[0]
        result.append({"时间": t.strftime(TIME_FORMAT), "price": price})
        t += datetime.timedelta(seconds=interval)
    return result


def main() -> None:
    print("=" * 50)
    print("            A 股历史股价查询器")
    print("=" * 50)

    # 1. 股票代码
    while True:
        raw = input("请输入股票代码（如 600519，输入 q 退出）：").strip()
        if not raw:
            continue
        if raw.lower() in ("q", "quit", "exit"):
            print("再见！")
            return
        try:
            symbol = normalize_code(raw)
            break
        except ValueError as e:
            print(f"[输入错误] {e}")

    # 2. 开始 / 结束时间
    while True:
        try:
            start = parse_time(input("请输入开始时间（如 2025-01-02 00:01:02）："))
            end = parse_time(input("请输入结束时间（如 2025-03-02 00:01:02）："))
        except ValueError as e:
            print(f"[输入错误] {e}")
            continue
        if start > end:
            print("[输入错误] 开始时间不能晚于结束时间")
            continue
        break

    # 3. 时间间隔（秒），并检查数据点数量
    while True:
        raw = input("请输入时间间隔（单位：秒，如 60）：").strip()
        if not (raw.isdigit() and int(raw) > 0):
            print("[输入错误] 间隔必须是正整数（秒）")
            continue
        interval = int(raw)
        n_points = int((end - start).total_seconds() // interval) + 1
        if n_points > MAX_POINTS:
            print(f"[输入错误] 将产生约 {n_points} 个数据点（上限 {MAX_POINTS}），请增大时间间隔")
            continue
        break

    # 4. 查询并展示结果
    result = query_prices(symbol, start, end, interval)
    if not result:
        print("[错误] 未获取到该股票的行情数据，请检查网络或代码是否正确。")
        return

    print(f"\n共 {len(result)} 个数据点：")
    for item in result:
        print(item)


if __name__ == "__main__":
    main()