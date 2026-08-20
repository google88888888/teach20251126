# 腾讯行情接口——1分钟历史数据

# 接口：https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,{time},{count}

# 参数
#     symbol: 替换成带市场前缀的股票代码，如 sh600519（贵州茅台）
#     m1:     固定写法(1分钟K线)
#     time:   替换成时间：年月日时分，如202608171121，可不填，位置要留（留空则取到最新交易分钟）
#     count:  返回从time开始最近的count根K线，如60

# 返回JSON结构
#     {
#         "code": 0,
#         "data": {
#             "sh600519": {
#                 "m1": [
#                     ["202608200931","开盘价","收盘价（看这个值即可，和百度搜出的一样）","最高价","最低价","成交量（单位手）","不用管这一列","不用管这一列"],
#                     ['202608171118', '1287.95', '1286.58', '1287.95', '1286.58', '119.50', {}, '0.0956']
#                     ['202608171119', '1286.58', '1286.96', '1287.00', '1285.81', '159.00', {}, '0.1272']
#                     ['202608171120', '1286.85', '1286.01', '1286.85', '1285.52', '129.00', {}, '0.1032']
#                 ]
#             }
#         }
#     }

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

symbol = normalize_code("sh600519")
if(symbol == None):
    print("请输入 6 位数字股票代码（如 600519），或带市场前缀（如 sh600519）")
else:
    # resp = requests.get(f"https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,,60")
    resp = requests.get(f"https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,{'202608171121'},{'3'}")
    data = resp.json()
    klines = data["data"][symbol]["m1"]
    for row in klines:
        print(row)