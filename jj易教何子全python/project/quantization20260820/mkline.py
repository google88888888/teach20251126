# 腾讯行情接口

# 接口：https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,time,count

# 参数
#     symbol: 替换成带市场前缀的股票代码，如 sh600519（贵州茅台）
#     m1:     固定写法(1分钟K线)
#     time:   替换成时间：年月日时分，如202608171121，可不填，位置要留
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

import requests

symbol = "sh600519"
# resp = requests.get(f"https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,,60")
resp = requests.get(f"https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,202608171121,3")
data = resp.json()
klines = data["data"][symbol]["m1"]
for row in klines:
    print(row)