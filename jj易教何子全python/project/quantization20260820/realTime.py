




import datetime
import re
import time
import requests

# 把用户输入股票代码规范为接口所需的市场前缀股票代码，如 600519 -> sh600519
def normalize_code(raw: str):
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
    return None

# A股交易时段：上午 9:30-11:30，下午 13:00-15:00
TRADING_SESSIONS = (
    (datetime.time(9, 30), datetime.time(11, 30)),
    (datetime.time(13, 0), datetime.time(15, 0)),
)

# 判断是否处于 A 股交易时段
def is_trading_time(now: datetime.datetime | None = None) -> bool:
    now = now or datetime.datetime.now()
    # 周六、周日休市
    if now.weekday() >= 5:                         
        return False
    t = now.time()
    return any(start <= t <= end for start, end in TRADING_SESSIONS)

# 请求腾讯行情接口并解析，返回行情字典；失败返回 None
def fetch_quote(symbol: str) -> dict | None:
    try:
        resp = requests.get(f"https://qt.gtimg.cn/q={symbol}")                  # 接口返回 GBK 编码
    except requests.RequestException:
        return None
    text = re.search(r'"([^"]+)"', resp.text)
    if not text:
        return None
    f = text.group(1).split("~")
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

symbol = normalize_code("sh600519")
if(symbol == None):
    print("请输入 6 位数字股票代码（如 600519），或带市场前缀（如 sh600519）")
else: