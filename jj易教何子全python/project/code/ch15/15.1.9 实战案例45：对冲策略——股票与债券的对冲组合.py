import backtrader as bt
import pandas as pd

# 定义对冲策略
class HedgeStrategy(bt.Strategy):
    def __init__(self):
        # 获取 AAPL 和 TLT 的数据
        self.aapl = self.datas[0]
        self.tlt = self.datas[1]

        # 设置初始资产配置比例（60% AAPL，40% TLT）
        self.aapl_target_weight = 0.6
        self.tlt_target_weight = 0.4

    def next(self):
        # 计算当前投资组合的总价值
        total_value = self.broker.getvalue()

        # 计算目标持仓价值
        aapl_target_value = total_value * self.aapl_target_weight
        tlt_target_value = total_value * self.tlt_target_weight

        # 获取当前持仓价值
        aapl_current_value = self.broker.getvalue([self.aapl])
        tlt_current_value = self.broker.getvalue([self.tlt])

        # 调整 AAPL 持仓
        if aapl_current_value < aapl_target_value:
            # 买入 AAPL
            aapl_amount = (aapl_target_value - aapl_current_value) / self.aapl.close[0]
            self.buy(data=self.aapl, size=aapl_amount)
        elif aapl_current_value > aapl_target_value:
            # 卖出 AAPL
            aapl_amount = (aapl_current_value - aapl_target_value) / self.aapl.close[0]
            self.sell(data=self.aapl, size=aapl_amount)

        # 调整 TLT 持仓
        if tlt_current_value < tlt_target_value:
            # 买入 TLT
            tlt_amount = (tlt_target_value - tlt_current_value) / self.tlt.close[0]
            self.buy(data=self.tlt, size=tlt_amount)
        elif tlt_current_value > tlt_target_value:
            # 卖出 TLT
            tlt_amount = (tlt_current_value - tlt_target_value) / self.tlt.close[0]
            self.sell(data=self.tlt, size=tlt_amount)

# 数据加载函数
def load_data():
    # 读取 CSV 文件
    df = pd.read_csv('data/HistoricalData_TLT_AAPL.csv', parse_dates=['Date'], index_col='Date')

    # 将数据转换为 backtrader 格式
    data_aapl = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引作为日期
        open='Open_AAPL',
        high='High_AAPL',
        low='Low_AAPL',
        close='Close_AAPL',
        volume='Volume_AAPL',
        openinterest=-1
    )
    data_tlt = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引作为日期
        open='Open_TLT',
        high='High_TLT',
        low='Low_TLT',
        close='Close_TLT',
        volume='Volume_TLT',
        openinterest=-1
    )
    return data_aapl, data_tlt

# 主程序
if __name__ == '__main__':
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()

    # 加载数据
    data_aapl, data_tlt = load_data()
    cerebro.adddata(data_aapl, name='AAPL')
    cerebro.adddata(data_tlt, name='TLT')

    # 添加策略
    cerebro.addstrategy(HedgeStrategy)

    # 设置初始资金
    cerebro.broker.set_cash(1000000)  # 初始资金 100 万元

    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.001)  # 0.1% 的交易手续费

    # 运行回测
    print('初始投资组合价值: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('最终投资组合价值: %.2f' % cerebro.broker.getvalue())

    # 绘制结果
    cerebro.plot()