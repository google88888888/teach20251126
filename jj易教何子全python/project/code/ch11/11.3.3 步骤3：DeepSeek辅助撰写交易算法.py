import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 假设我们有一个1分钟间隔的价格数据（示例数据），你可以用真实的金融数据代替
# 模拟1分钟频率的股价数据
np.random.seed(42)
minutes = 1000
time_index = pd.date_range('2025-01-01', periods=minutes, freq='T')
price_data = np.cumsum(np.random.randn(minutes)) + 100  # 累加生成价格波动

# 将数据放入DataFrame中
data = pd.DataFrame({'Time': time_index, 'Price': price_data})
data.set_index('Time', inplace=True)

# 设置SMA窗口：短期SMA和长期SMA
short_window = 5   # 短期SMA窗口（例如5分钟）
long_window = 20  # 长期SMA窗口（例如20分钟）

# 计算短期SMA和长期SMA
data['Short_SMA'] = data['Price'].rolling(window=short_window).mean()
data['Long_SMA'] = data['Price'].rolling(window=long_window).mean()

# 初始化买入/卖出信号
data['Signal'] = 0
data['Signal'][data['Short_SMA'] > data['Long_SMA']] = 1  # 短期SMA突破长期SMA时买入信号
data['Signal'][data['Short_SMA'] < data['Long_SMA']] = -1  # 短期SMA下穿长期SMA时卖出信号

# 计算持仓
data['Position'] = data['Signal'].shift()  # 将买卖信号移到下一周期，表示在当前周期执行操作

# 计算策略的收益
data['Daily_Return'] = data['Price'].pct_change()  # 市场的实际收益
data['Strategy_Return'] = data['Daily_Return'] * data['Position']  # 策略收益 = 实际收益 * 持仓信号

# 计算累计收益
data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()
data['Cumulative_Market_Return'] = (1 + data['Daily_Return']).cumprod()

# 绘制策略和市场的累计收益对比
plt.figure(figsize=(10, 6))
plt.plot(data['Cumulative_Strategy_Return'], label='Strategy Return', color='blue')
plt.plot(data['Cumulative_Market_Return'], label='Market Return', color='red')
plt.title(f"Momentum Strategy vs Market Performance")
plt.legend()
plt.show()

# 输出最后的策略表现
print(f"最终策略收益：{data['Cumulative_Strategy_Return'].iloc[-1]:.2f}")
print(f"市场累计收益：{data['Cumulative_Market_Return'].iloc[-1]:.2f}")
