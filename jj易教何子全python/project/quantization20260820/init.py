# -*- coding: utf-8 -*-
"""
实时股票行情查看器

功能：
    1. 输入股票代码（如 600519 / 000001 / 300750，或 sh600519）
    2. 交易时段内每隔几秒实时刷新显示股价
    3. 非交易时段（周末、节假日、开盘前、收盘后、停牌）显示"暂无交易"

数据来源：腾讯免费行情接口 qt.gtimg.cn

接口返回完整示例（resp.text，GBK 解码后的字符串，以 sh600519 为例）：
    v_sh600519="1~贵州茅台~600519~1291.79~1307.88~1299.80~15318~6402~8909~1291.35~2~1291.33~1~1291.30~5~1291.28~1~1291.26~2~1291.86~2~1291.87~4~1292.00~1~1292.20~1~1292.46~1~~20260820112228~-16.09~-1.23~1306.88~1291.00~1291.79/15318/1986540868~15318~198654~0.12~19.83~~1306.88~1291.00~1.21~16148.43~16148.43~6.43~1438.67~1177.09~0.75~2~1296.85~18.14~19.62~~~0.15~198654.0868~0.0000~0~   A~GP-A~-4.25~-4.69~4.03~32.41~27.30~1539.98~1151.01~-1.28~-0.02~1.32~1250081601~1250081601~10.00~-7.73~1250081601~~~-7.60~-0.00~~CNY~0~___D__F__N~1291.20~13~";

    结构说明：
    - 整体是一个 JS 变量赋值语句：v_股票代码="~分隔的字段串";
    - 代码用正则取双引号内的部分，再按 ~ split 成列表 f（共 88 个元素）
    - 常用字段下标对照（f[下标] -> 含义）：
        f[0]  未知/类别(1)          f[1]  名称(贵州茅台)
        f[2]  代码(600519)          f[3]  当前价(1291.79)
        f[4]  昨收(1307.88)         f[5]  今开(1299.80)
        f[6]  成交量(手)            f[7]  外盘            f[8]  内盘
        f[9]~f[28]  买一~买五/卖一~卖五（价格~数量 成对出现）
        f[30] 行情时间(yyyymmddHHMMSS，如 20260820112228)
        f[31] 涨跌额(-16.09)        f[32] 涨跌幅%(-1.23)
        f[33] 最高(1306.88)         f[34] 最低(1291.00)
        f[36] 成交量(手,15318)      f[37] 成交额(万元,198654)
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
            # timeout=TIMEOUT,
            # headers={"User-Agent": "Mozilla/5.0"},
        )
        # resp.encoding = "gbk"                      # 接口返回 GBK 编码
    except requests.RequestException:
        return None
    print(resp.text)
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


def parse_quote_time(q: dict | None) -> datetime.datetime | None:
    """把 q["quote_time"]（yyyymmddHHMMSS）解析为 datetime；q 为空或格式异常时返回 None"""
    if not q:
        return None
    try:
        return datetime.datetime.strptime(q["quote_time"], "%Y%m%d%H%M%S")
    except (KeyError, TypeError, ValueError):
        return None


def build_line(now: datetime.datetime, q: dict) -> str:
    """交易中：拼接单行实时行情文本（时间优先用行情自带 quote_time，避免本地时钟误差）"""
    try:
        change = float(q["change"])
    except (TypeError, ValueError):
        change = 0.0
    arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
    quote_dt = parse_quote_time(q) or now                # 行情时间缺失时回退本地时间
    return (
        f'{quote_dt:%H:%M:%S} {q["name"]}({q["code"]}) '
        f'现价 {q["price"]} {arrow}{q["change"]} ({q["change_pct"]}%) | '
        f'今开 {q["open"]} 最高 {q["high"]} 最低 {q["low"]} 昨收 {q["prev_close"]}'
    )


def monitor(symbol: str, max_refreshes: int | None = None) -> None:
    """主循环：所有判断均以行情自带时间 quote_time 为准，不依赖本地时钟"""
    print(f"开始监控 {symbol}，每 {REFRESH_INTERVAL} 秒刷新一次，按 Ctrl+C 退出\n")
    n = 0
    try:
        while max_refreshes is None or n < max_refreshes:
            # 所有判断均基于行情自带时间 quote_time，不使用本地时间
            q = fetch_quote(symbol)
            quote_dt = parse_quote_time(q)              # 行情时间；获取失败/格式异常时为 None

            if quote_dt is None:
                msg = "暂无交易（行情获取失败，请检查网络）"
            elif not is_trading_time(quote_dt):         # 周末/时段判断都用行情时间
                msg = "暂无交易（行情时间不在交易时段）"
            elif float(q["open"] or 0) == 0:
                msg = "暂无交易（今日无成交，可能停牌）"
            else:
                msg = None

            stamp = quote_dt or datetime.datetime.now()  # 仅作显示兜底，不参与任何判断
            if msg:
                print(f"\r{stamp:%Y-%m-%d %H:%M:%S}  {msg}", end="", flush=True)
            else:
                print("\r\033[K" + build_line(stamp, q), end="", flush=True)

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