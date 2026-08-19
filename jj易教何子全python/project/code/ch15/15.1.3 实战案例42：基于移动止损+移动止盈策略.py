import pandas as pd
import backtrader as bt

# ================= 数据加载与清洗 =================

# 加载本地股票数据文件
data = pd.read_csv("Data/HistoricalData_AAPL.csv", parse_dates=True, index_col="Date")

# 数据清洗：列名标准化和格式处理
for col in ["Close/Last", "Open", "High", "Low"]:
    data[col] = data[col].replace({'\$': '', ',': ''}, regex=True).astype(float)

data.rename(columns={"Close/Last": "Close"}, inplace=True)  # 统一列名为Backtrader标准格式
# 确保数据按日期升序排列
data = data.sort_index()


# ================= Backtrader 策略实现 =================

class TrailingStopTake(bt.Strategy):
    params = (
        ('stop_trail_pct', 0.05),  # 移动止损比例5%
        ('take_trail_pct', 0.10),  # 移动止盈比例10%
        ('ma_period', 20),        # 20日均线
    )

    def __init__(self):
        # 计算20日均线
        self.sma20 = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_period
        )
        self.highest_price = None  # 记录最高价
        self.buy_price = None      # 记录买入价格

    def next(self):
        # 获取当前日期
        dt = self.datas[0].datetime.date(0)

        # 打印当前价格和20日均线
        print(f"{dt}, 当前价: {self.data.close[0]:.2f}, 20日均线: {self.sma20[0]:.2f}")

        if not self.position:  # 如果没有持仓
            if self.data.close[0] > self.sma20[0]:  # 价格上穿20日均线
                print(f"{dt}, 买入信号触发！当前价: {self.data.close[0]:.2f}, 20日均线: {self.sma20[0]:.2f}")
                self.buy(size=100)  # 买入100股
                self.buy_price = self.data.close[0]  # 记录买入价格
                self.highest_price = self.data.close[0]  # 初始化最高价
        else:
            # 更新最高价
            self.highest_price = max(self.highest_price, self.data.close[0])

            # 计算移动止损和移动止盈价格
            stop_price = self.highest_price * (1 - self.params.stop_trail_pct)
            take_profit_price = self.highest_price * (1 + self.params.take_trail_pct)
            print(f"{dt}, 当前价: {self.data.close[0]:.2f}, 最高价: {self.highest_price:.2f}, 移动止损价: {stop_price:.2f}, 移动止盈价: {take_profit_price:.2f}")

            # 检查是否触发移动止损或移动止盈
            if self.data.close[0] < stop_price or self.data.close[0] > take_profit_price:
                print(f"{dt}, 卖出信号触发！当前价: {self.data.close[0]:.2f}, 移动止损价: {stop_price:.2f}, 移动止盈价: {take_profit_price:.2f}")
                self.sell(size=100)  # 卖出100股
                self.highest_price = None  # 重置最高价
                self.buy_price = None      # 重置买入价格

# ================= 回测设置与运行 =================

if __name__ == "__main__":
    # 初始化回测引擎
    cerebro = bt.Cerebro()

    # 添加策略
    cerebro.addstrategy(TrailingStopTake)

    # 将Pandas数据转换为Backtrader数据格式
    data_feed = bt.feeds.PandasData(
        dataname=data,
        fromdate=data.index.min(),  # 数据起始日期
        todate=data.index.max(),    # 数据结束日期
        timeframe=bt.TimeFrame.Days  # 数据时间粒度（日线）
    )
    cerebro.adddata(data_feed)  # 将数据注入引擎

    # 配置回测参数
    cerebro.broker.set_cash(100000.0)          # 设置初始资金为100,000美元
    cerebro.broker.setcommission(commission=0.001)  # 设置交易佣金为0.1%

    # 执行回测并输出结果
    print("初始资金: %.2f" % cerebro.broker.getvalue())
    cerebro.run()  # 运行回测
    print("最终资金: %.2f" % cerebro.broker.getvalue())
    cerebro.plot()  # 可视化回测结果