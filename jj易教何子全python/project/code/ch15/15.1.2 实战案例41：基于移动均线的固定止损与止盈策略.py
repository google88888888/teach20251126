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
class FixedStopTake(bt.Strategy):
    params = (
        ('stop_loss_pct', 0.05),  # 止损比例5% 
        ('take_profit_pct', 0.10), # 止盈比例10% 
        ('ma_period', 20),        # 20日均线       
    )
    def __init__(self):
        # 计算20日均线
        self.ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_period
        )
        self.buy_price = None  # 记录买入价格

    def next(self):
        if not self.position:  # 如果没有持仓
            # 买入条件：价格上穿20日均线
            if self.data.close[0] > self.ma[0]:
                self.buy(size=100)  # 买入100股
                self.buy_price = self.data.close[0]  # 记录买入价格
        else:
            # 计算固定止损和止盈价格
            stop_price = self.buy_price * (1 - self.params.stop_loss_pct)
            take_profit_price = self.buy_price * (1 + self.params.take_profit_pct)

            # 卖出条件：触发止损或止盈
            if self.data.close[0] < stop_price or self.data.close[0] > take_profit_price:
                self.sell(size=self.position.size)  # 卖出全部持仓
                self.buy_price = None  # 重置买入价格
# ================= 回测设置与运行 =================
if __name__ == "__main__":
    # 初始化回测引擎
    cerebro = bt.Cerebro()

    # 添加策略
    cerebro.addstrategy(FixedStopTake)

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