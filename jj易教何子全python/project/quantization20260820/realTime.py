# 腾讯行情接口——实时数据

# 接口：https://qt.gtimg.cn/q={symbol}

# 参数
#     symbol: 替换成带市场前缀的股票代码，如 sh600519（贵州茅台）

# resp.text之后返回字符串，以 sh600519（贵州茅台）为例
#     v_sh600519="1~贵州茅台~600519~1291.79~1307.88~1299.80~15318~6402~8909~1291.35~2~1291.33~1~1291.30~5~1291.28~1~1291.26~2~1291.86~2~1291.87~4~1292.00~1~1292.20~1~1292.46~1~~20260820112228~-16.09~-1.23~1306.88~1291.00~1291.79/15318/1986540868~15318~198654~0.12~19.83~~1306.88~1291.00~1.21~16148.43~16148.43~6.43~1438.67~1177.09~0.75~2~1296.85~18.14~19.62~~~0.15~198654.0868~0.0000~0~   A~GP-A~-4.25~-4.69~4.03~32.41~27.30~1539.98~1151.01~-1.28~-0.02~1.32~1250081601~1250081601~10.00~-7.73~1250081601~~~-7.60~-0.00~~CNY~0~___D__F__N~1291.20~13~";

#     结构说明：
#     - 整体是：v_股票代码="~分隔的字段串";
#     - 代码用正则取双引号内的部分，再按 ~ split 成列表 text_split_value（共 88 个元素）
#     - 常用字段下标对照（text_split_value[下标] -> 含义）：
#         text_split_value[0]  未知/类别(1)          
#         text_split_value[1]  名称(贵州茅台)
#         text_split_value[2]  代码(600519)          
#         text_split_value[3]  当前价(1291.79)
#         text_split_value[4]  昨收(1307.88)         
#         text_split_value[5]  今开(1299.80)
#         text_split_value[6]  成交量(手)            
#         text_split_value[7]  外盘            
#         text_split_value[8]  内盘
#         text_split_value[9]~text_split_value[28]  买一~买五/卖一~卖五（价格~数量 成对出现）
#         text_split_value[30] 行情时间(yyyymmddHHMMSS，如 20260820112228)
#         text_split_value[31] 涨跌额(-16.09)        
#         text_split_value[32] 涨跌幅%(-1.23)
#         text_split_value[33] 最高(1306.88)         
#         text_split_value[34] 最低(1291.00)
#         text_split_value[36] 成交量(手,15318)      
#         text_split_value[37] 成交额(万元,198654)

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

# 刷新间隔（秒）
REFRESH_INTERVAL = 3

# 判断是否处于 A 股交易时段
def is_trading_time(now: datetime.datetime) -> bool:
    # 周六、周日休市
    if now.weekday() >= 5:                         
        return False
    t = now.time()
    return any(start <= t <= end for start, end in TRADING_SESSIONS)

# 请求腾讯行情接口并解析，成功返回字典，失败返回None
def fetch_quote(symbol: str) -> dict | None:
    try:
        resp = requests.get(f"https://qt.gtimg.cn/q={symbol}")                  # 接口返回 GBK 编码
    except requests.RequestException:
        return None
    text = re.search(r'"([^"]+)"', resp.text)
    if not text:
        return None
    text_without_quotation_marks=text.group(1)
    text_split_value = text_without_quotation_marks.split("~")
    if len(text_split_value) < 38 or not text_split_value[3]:
        return None
    return {
        "name": text_split_value[1],           # 名称
        "code": text_split_value[2],           # 代码
        "price": text_split_value[3],          # 当前价
        "prev_close": text_split_value[4],     # 昨收
        "open": text_split_value[5],           # 今开
        "quote_time": text_split_value[30],    # 行情时间 yyyymmddHHMMSS
        "change": text_split_value[31],        # 涨跌额
        "change_pct": text_split_value[32],    # 涨跌幅 %
        "high": text_split_value[33],          # 最高
        "low": text_split_value[34],           # 最低
        "volume": text_split_value[36],        # 成交量（手）
        "amount": text_split_value[37],        # 成交额（万元）
    }

# 把 real_time_data["quote_time"]（yyyymmddHHMMSS）解析为 datetime；real_time_data 为空或格式异常时返回 系统当前时间
def parse_quote_time(real_time_data: dict | None) -> datetime.datetime:
    if not real_time_data:
        print('real_time_data为空，使用系统当前时间')
        return datetime.datetime.now()
    try:
        return datetime.datetime.strptime(real_time_data["quote_time"], "%Y%m%d%H%M%S")
    except (KeyError, TypeError, ValueError):
        print('real_time_data格式异常，使用系统当前时间')
        return datetime.datetime.now()

# 展示实时行情文本
def build_line(real_time_data: dict) -> str:
    try:
        change = float(real_time_data["change"])
    except (TypeError, ValueError):
        change = 0.0
    arrow='→'
    if change > 0:
        arrow = "↑"
    elif change < 0:
        arrow = "↓"
    quote_dt = parse_quote_time(real_time_data)
    return (
        f'{quote_dt:%Y-%m-%d %H:%M:%S} {real_time_data["name"]}({real_time_data["code"]}) '
        f'现价 {real_time_data["price"]} {arrow}{real_time_data["change"]} ({real_time_data["change_pct"]}%) | '
        f'今开 {real_time_data["open"]} 最高 {real_time_data["high"]} 最低 {real_time_data["low"]} 昨收 {real_time_data["prev_close"]}'
    )

# 主循环
def monitor(symbol: str) -> None:
    print(f"开始监控 {symbol}，每 {REFRESH_INTERVAL} 秒刷新一次")
    while True:
        real_time_data = fetch_quote(symbol)
        quote_dt = parse_quote_time(real_time_data)
        if not is_trading_time(quote_dt):
            msg = "暂无交易（行情时间不在交易时段）"
        elif float(real_time_data["open"] or 0) == 0:
            msg = "暂无交易（今日无成交，可能停牌）"
        else:
            msg = None
        if msg:
            print(f"{quote_dt:%Y-%m-%d %H:%M:%S} {msg}")
        else:
            print(build_line(real_time_data))
        time.sleep(REFRESH_INTERVAL)


symbol = normalize_code("sh600519")
if(symbol == None):
    print("请输入 6 位数字股票代码（如 600519），或带市场前缀（如 sh600519）")
else:
    monitor(symbol)
