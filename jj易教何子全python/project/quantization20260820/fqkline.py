# 腾讯行情接口——日K线历史数据（前复权）

# 接口：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,{start},{end},{count},qfq

# 参数
#     symbol: 替换成带市场前缀的股票代码，如 sh600519（贵州茅台）
#     day:    固定写法(日K线)
#     start:  替换成开始日期，如 2026-08-01，可不填，位置要留（留空则从能取到的最早日期开始）
#     end:    替换成结束日期，如 2026-08-20，可不填，位置要留（留空则取到最新交易日）
#     count:  最多返回的K线数量，如 2
#     qfq:    固定写法，复权方式：qfq=前复权（看这个即可，和百度搜出的历史价格一致），hfq=后复权，留空=不复权

# 返回JSON结构
#     注意：复权方式不同，键名不同——qfq 对应 qfqday，hfq 对应 hfqday，不复权对应 day
#     {
#         "code": 0,
#         "data": {
#             "sh600519": {
#                 "qfqday": [
#                     ["日期","开盘价","收盘价（看这个值即可，和百度搜出的一样）","最高价","最低价","成交量（单位手）"],
#                     ['2026-08-17', '1295.000', '1293.090', '1301.000', '1280.340', '78430.000']
#                     ['2026-08-18', '1291.000', '1297.990', '1302.900', '1285.170', '38723.000']
#                     ['2026-08-19', '1300.000', '1307.880', '1308.880', '1290.500', '37548.000']
#                 ]
#             }
#         }
#     }

import re
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
    # resp = requests.get(f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,{''},{''},2,qfq")
    resp = requests.get(f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,{"2026-08-03"},{"2026-08-6"},2,qfq")
    data = resp.json()
    klines = data["data"][symbol]["qfqday"]        # 前复权取 qfqday；后复权取 hfqday；不复权取 day
    for row in klines:
        print(row)