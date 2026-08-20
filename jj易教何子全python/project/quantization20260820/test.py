# -*- coding: utf-8 -*-
"""
腾讯行情接口 mkline 最简用法示例

接口：https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={symbol},m1,,320
    - symbol: 带市场前缀的股票代码，如 sh600519（贵州茅台）
    - m1:     1分钟K线
    - 320:    返回最近的 320 根K线

注意：
    原域名 web.ifzq.gtimg.cn 已 301 跳转到 web3.ifzq.gtimg.cn，
    而 web3 域名已无 DNS 解析，因此直接使用 ifzq.gtimg.cn。

返回 JSON 结构（节选）：
    {
        "code": 0,
        "data": {
            "sh600519": {
                "m1": [
                    ["202608200931", "开盘", "收盘（当前分钟的看这个值即可，和百度一样）", "最高", "最低", "成交量（单位手）", 不用管这一列,不用管这一列],
                    ...
                ]
            }
        }
    }
"""

import requests

URL = (
    "https://ifzq.gtimg.cn/appstock/app/kline/mkline"
    "?param={symbol},m1,,320"
    # "?param={symbol},m1,202608171121,320"
)

# trust_env=False：不使用系统/环境变量里的代理，直接连接
# session = requests.Session()
# session.trust_env = False

symbol = "sh600519"
resp = requests.get(URL.format(symbol=symbol), timeout=10)
data = resp.json()

klines = data["data"][symbol]["m1"]
print(f"共获取 {len(klines)} 根 1 分钟K线，最后 5 根：")
for row in klines:
    # row: [时间, 开盘, 收盘, 最高, 最低, 成交量]
    print(row)