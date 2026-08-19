import pandas as pd
import backtrader as bt
import numpy as np


# ================= 数据加载与清洗 =================
# 加载本地股票数据文件
data = pd.read_csv("Data/HistoricalData_TSLA.csv", parse_dates=True, index_col="Date")

# 数据清洗：列名标准化和格式处理
for col in ["Close/Last", "Open", "High", "Low"]:
    # 去掉价格字段中的美元符号和逗号，并转换为浮点数
    data[col] = data[col].replace({'\$': '', ',': ''}, regex=True).astype(float)

# 统一列名为 Backtrader 标准格式
data.rename(columns={"Close/Last": "Close"}, inplace=True)

# 确保数据按日期升序排列
data = data.sort_index()



# ================= 动态头寸管理策略 =================
class DynamicPositionManagement(bt.Strategy):
    """
    基于波动率的动态头寸管理策略
    - 使用 ATR 动态调整仓位大小
    - 设置止损和止盈
    """
    params = (
        ('risk_per_trade', 0.02),  # 每笔交易风险比例（账户资金的2%）
        ('stop_loss', 0.05),  # 止损比例（5%）
        ('take_profit', 0.10),  # 止盈比例（10%）
        ('atr_period', 14),  # ATR周期（用于波动率计算）
    )

    def __init__(self):
        """
        初始化策略
        """
        # 初始化 ATR 和 SMA 指标
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)  # ATR指标
        self.sma = bt.indicators.SMA(self.data.close, period=20)  # 20日简单移动平均线

        # 跟踪交易状态
        self.order = None  # 当前订单
        self.entry_price = None  # 入场价格

        # 初始化资金记录
        self.value_log = []  # 记录每日资金变化

    def next(self):
        """
        每个交易日调用的逻辑
        """
        # 如果有未完成的订单，跳过
        if self.order:
            return

        # 检查数据长度是否足够计算 SMA
        if len(self.data.close) < self.params.atr_period:
            return

        # 记录每日资金
        self.value_log.append(self.broker.getvalue())

        # 如果没有持仓，检查买入条件
        if not self.position:
            self._check_buy()
        # 如果有持仓，检查卖出条件
        else:
            self._check_sell()

    def _check_buy(self):
        """
        检查买入条件
        """
        # 简单的买入信号：价格上穿20日均线
        if self.data.close[0] > self.sma[0]:
            # 计算仓位大小
            risk_amount = self.broker.getvalue() * self.params.risk_per_trade  # 风险金额
            position_size = risk_amount / (self.atr[0] * self.params.stop_loss)  # 仓位大小

            # 执行买入
            self.order = self.buy(size=position_size)
            self.entry_price = self.data.close[0]  # 记录入场价格
            print(f"{self.data.datetime.date(0)} 买入 {position_size:.2f} 股 @ {self.entry_price:.2f}")

    def _check_sell(self):
        """
        检查卖出条件
        """
        current_price = self.data.close[0]

        # 计算止损和止盈价格
        stop_loss_price = self.entry_price * (1 - self.params.stop_loss)
        take_profit_price = self.entry_price * (1 + self.params.take_profit)

        # 检查是否触发止损或止盈
        if current_price <= stop_loss_price or current_price >= take_profit_price:
            self.order = self.close()  # 平仓
            print(f"{self.data.datetime.date(0)} 平仓 @ {current_price:.2f}")
            self.entry_price = None  # 重置入场价格

    def notify_order(self, order):
        """
        订单状态通知
        """
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None  # 重置订单状态

    def stop(self):
        """
        回测结束后调用，计算绩效指标
        """
        # 计算绩效指标
        if len(self.value_log) > 1:
            returns = pd.Series(self.value_log).pct_change().dropna()  # 每日收益率
            sharpe = returns.mean() / returns.std() * np.sqrt(252)  # 夏普比率
            max_drawdown = (pd.Series(self.value_log) / pd.Series(self.value_log).cummax() - 1).min()  # 最大回撤
        else:
            sharpe = np.nan
            max_drawdown = np.nan

        # 输出绩效指标
        print(f"\n=== 最终绩效 ===")
        print(f"夏普比率: {sharpe:.2f}")
        print(f"最大回撤: {max_drawdown:.2%}")
        print(f"最终资金: {self.broker.getvalue():.2f}")


# ================= 执行回测 =================
if __name__ == '__main__':
    # 初始化回测引擎
    cerebro = bt.Cerebro()

    # 将 Pandas 数据转换为 Backtrader 数据格式
    data_feed = bt.feeds.PandasData(
        dataname=data,
        datetime=None,  # 使用默认索引（日期）
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',  # 成交量数据
        openinterest=None  # 未平仓量（可选）
    )
    cerebro.adddata(data_feed)  # 添加数据

    # 添加策略
    cerebro.addstrategy(DynamicPositionManagement)

    # 配置初始资金和佣金
    cerebro.broker.setcash(100000)  # 初始资金 100,000 美元
    cerebro.broker.setcommission(commission=0.001)  # 佣金 0.1%

    # 运行回测
    print('初始资金:', cerebro.broker.getvalue())
    cerebro.run()  # 运行回测
    print('最终资金:', cerebro.broker.getvalue())

    # 绘制结果
    cerebro.plot(style='candlestick')