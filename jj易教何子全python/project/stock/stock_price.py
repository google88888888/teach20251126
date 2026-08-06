# -*- coding: utf-8 -*-
"""
实时获取任意一只股票（A股/港股/美股）的最新价格并打印。

数据来源：腾讯财经实时行情接口（无需 token，稳定）
接口示例：
    沪市股票：sh600519（贵州茅台）
    深市股票：sz000001（平安银行）
    港股：     hk00700（腾讯控股）
    美股：     usAAPL（苹果公司）

使用方法：
    1) 作为模块函数调用
        from stock_price import get_realtime_price
        print(get_realtime_price("600519"))
    2) 命令行直接运行
        python stock_price.py 600519
        python stock_price.py 000001
"""

import sys
import time

import requests


# 腾讯财经实时行情接口
TENCENT_QUOTE_URL = "https://qt.gtimg.cn/q={symbol}"


def to_market_symbol(code: str) -> str:
    """根据股票代码自动判断市场，并拼接成腾讯接口需要的前缀格式。

    A股规则：
        6 开头 -> 沪市 sh
        0、3 开头 -> 深市 sz
        8、4 开头 -> 北交所 bj
    港股/美股直接返回原值（如 hk00700、usAAPL）。
    """
    code = code.strip().lower()

    # 已经带市场前缀的，直接返回
    if code.startswith(("sh", "sz", "bj", "hk", "us")):
        return code

    if not code.isdigit():
        # 非纯数字且没有前缀，按美股处理
        return "us" + code.upper()

    # 纯数字的 A 股代码
    if code.startswith("6"):
        return "sh" + code
    if code.startswith(("0", "3")):
        return "sz" + code
    if code.startswith(("8", "4")):
        return "bj" + code
    return "sz" + code  # 默认深市


def get_realtime_price(code: str, timeout: int = 5) -> dict:
    """获取指定股票的实时行情。

    返回字典字段说明：
        code        股票代码（带市场前缀，如 sh600519）
        name        股票名称
        price       最新价（float）
        pre_close   昨收（float）
        change      涨跌额（float）
        change_pct  涨跌幅（%，float）
        time        数据时间
    """
    symbol = to_market_symbol(code)
    url = TENCENT_QUOTE_URL.format(symbol=symbol)

    # 腾讯接口返回 GBK 编码文本
    resp = requests.get(url, timeout=timeout)
    resp.encoding = "gbk"
    text = resp.text.strip()

    # 接口在无数据时返回类似：v_sh600519="";
    if '=""' in text or text.endswith('=""'):
        raise ValueError(f"未查询到股票 [{code}] 的行情，请检查代码是否正确。")

    # 示例返回：
    # v_sh600519="1~贵州茅台~600519~1685.00~1680.00~1688.00~..."
    body = text.split('"', 2)[1]
    fields = body.split("~")

    name = fields[1]
    current = float(fields[3])
    pre_close = float(fields[4])
    change = round(current - pre_close, 4)
    change_pct = round((change / pre_close) * 100, 4) if pre_close else 0.0
    data_time = fields[30] if len(fields) > 30 else time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "code": symbol,
        "name": name,
        "price": current,
        "pre_close": pre_close,
        "change": change,
        "change_pct": change_pct,
        "time": data_time,
    }


def print_realtime_price(code: str) -> None:
    """获取并打印一只股票的实时价格。"""
    info = get_realtime_price(code)
    print(code,info,'ffffffffffffffffffffffffffff')
    print(
        f"[{info['time']}] {info['name']}({info['code']}) "
        f"最新价：{info['price']}  "
        f"涨跌：{info['change']:+.2f} ({info['change_pct']:+.2f}%)"
    )


if __name__ == "__main__":
    # 默认演示贵州茅台，也可通过命令行参数指定任意股票代码
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "600519"
    print_realtime_price(stock_code)
