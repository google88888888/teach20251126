# 导入必要的库
import backtrader as bt  # 量化回测框架
import pandas as pd  # 数据处理库
import datetime  # 时间处理库


# 定义双均线策略类
class DualMovingAverageStrategy(bt.Strategy):
    # 策略参数：短期5日均线，长期10日均线
    params = (
        ("short_period", 5),  # 短期均线周期（默认5天）
        ("long_period", 10),  # 长期均线周期（默认10天）
    )

    def __init__(self):
        # 计算短期和长期简单移动平均线（SMA）
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )

    def next(self):
        """生成交易信号"""
        if self.sma_short > self.sma_long and not self.position:
            self.buy()  # 买入信号
        elif self.sma_short < self.sma_long and self.position:
            self.sell()  # 卖出信号


if __name__ == "__main__":
    # 加载本地股票数据文件
    data = pd.read_csv("data/AAPL.csv", parse_dates=True, index_col="Date")
    # 列名标准化
    data.rename(columns={"Close/Last": "Close"}, inplace=True)
    # 处理特殊字符（例如 $123.45 -> 123.45）
    for col in ["Close", "Open", "High", "Low"]:
        data[col] = data[col].replace({'\$': '', ',': ''}, regex=True).astype(float)
    data = data.sort_index()  # 按日期排序

    # 初始化回测引擎
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DualMovingAverageStrategy)  # 注入策略
    # 转换数据为Backtrader格式
    data_feed = bt.feeds.PandasData(
        dataname=data,
        fromdate=data.index.min(),  # 起始日期
        todate=data.index.max(),  # 结束日期
        timeframe=bt.TimeFrame.Days  # 日线数据
    )
    cerebro.adddata(data_feed)  # 注入数据

    # 设置初始资金和佣金
    cerebro.broker.set_cash(10000.0)  # 初始资金10,000美元
    cerebro.broker.setcommission(commission=0.001)  # 佣金0.1%
    # 运行回测
    print("初始资金: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("最终资金: %.2f" % cerebro.broker.getvalue())

    # 可视化结果
    cerebro.plot()
