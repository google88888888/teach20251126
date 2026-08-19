
import backtrader as bt
import pandas as pd
import numpy as np

# 定义双均线策略
class DualMovingAverageStrategy(bt.Strategy):
    params = (
        ('sma_short', 5),   # 短期均线
        ('sma_long', 60),   # 长期均线
    )

    def __init__(self):
        # 定义短期和长期均线
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_short)
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_long)

    def next(self):
        # 如果短期均线上穿长期均线，买入
        if not self.position and self.sma_short > self.sma_long:
            self.buy()
        # 如果短期均线下穿长期均线，卖出
        elif self.position and self.sma_short < self.sma_long:
            self.sell()

    def stop(self):
        # 策略结束时记录绩效指标
        self.log_return = self.broker.get_value() / self.broker.startingcash - 1
        self.max_drawdown = self.stats.drawdown.maxdrawdown[-1]
        self.sharpe_ratio = self.stats.sharperatio.sharperatio[-1]

# 加载数据
def load_data():
    # 假设数据文件为 hs300.csv，包含 date 和 close 列
    data = pd.read_csv('hs300.csv', index_col='date', parse_dates=True)
    data = bt.feeds.PandasData(dataname=data)
    return data

# 参数优化函数
def optimize_strategy():
    # 定义参数范围
    sma_short_range = range(3, 21, 1)  # 短期均线范围：3到20天
    sma_long_range = range(50, 201, 10)  # 长期均线范围：50到200天，步长10

    # 存储优化结果
    results = []

    # 遍历所有参数组合
    for sma_short in sma_short_range:
        for sma_long in sma_long_range:
            if sma_short >= sma_long:
                continue  # 跳过短期均线大于等于长期均线的情况

            # 初始化 Cerebro 引擎
            cerebro = bt.Cerebro()
            cerebro.adddata(load_data())
            cerebro.addstrategy(DualMovingAverageStrategy, sma_short=sma_short, sma_long=sma_long)

            # 添加绩效分析
            cerebro.addanalyzer(bt.analyzers.Returns)
            cerebro.addanalyzer(bt.analyzers.DrawDown)
            cerebro.addanalyzer(bt.analyzers.SharpeRatio)

            # 运行回测
            result = cerebro.run()

            # 提取绩效指标
            strat = result[0]
            annual_return = strat.analyzers.returns.get_analysis()['rnorm100']  # 年化收益率（%）
            max_drawdown = strat.analyzers.drawdown.get_analysis()['max']['drawdown']  # 最大回撤（%）
            sharpe_ratio = strat.analyzers.sharperatio.get_analysis()['sharperatio']  # 夏普比率

            # 记录结果
            results.append({
                'sma_short': sma_short,
                'sma_long': sma_long,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
            })

    # 将结果保存为 DataFrame
    results_df = pd.DataFrame(results)
    results_df.to_csv('optimization_results.csv', index=False)
    print("优化完成，结果已保存到 optimization_results.csv")
# 运行优化
if __name__ == '__main__':
    optimize_strategy()
