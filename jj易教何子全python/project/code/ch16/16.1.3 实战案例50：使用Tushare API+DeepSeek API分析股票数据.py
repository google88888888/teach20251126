import tushare as ts
import pandas as pd
import re
from openai import OpenAI

# ---------------------------
# 1. 利用 Tushare 获取股票数据并计算描述性统计信息
# ---------------------------
# 初始化 Tushare pro 接口（请替换为你自己的 token）
pro = ts.pro_api('<修改为自己的TOKEN>')

# 获取指定股票的日线数据（此处以600519.SH为例，时间段可自行调整）
df = pro.daily(ts_code='600519.SH', start_date='20230101', end_date='20230701')

# 计算描述性统计信息，并转换为字符串格式
desc = df.describe()
desc_str = desc.to_string()

# ---------------------------
# 2. 使用 DeepSeek API 对描述性统计信息进行智能分析
# ---------------------------
# 初始化 DeepSeek 客户端（API Key 与 base_url 根据实际情况配置）
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# 构造请求消息，将描述性统计信息作为用户输入发送给智能体
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"请对下面的股票数据描述性统计信息进行详细分析，并给出投资建议：\n\n{desc_str}"}
    ],
    stream=False
)

# 获取 DeepSeek 返回的结果
input_str = response.choices[0].message.content
print("\nDeepSeek 返回的完整响应:")
print(input_str)
