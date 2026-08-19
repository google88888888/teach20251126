import pandas as pd       # 数据处理
import backtrader as bt   # 量化回测框架
import numpy as np        # 数值计算

# ================= 数据强化处理模块 =================
def load_data(filepath):
    """
    强化数据加载函数
    功能：从CSV文件加载并清洗股票和黄金数据
    
    参数：
        filepath (str): 数据文件路径
        
    返回：
        (pd.DataFrame, pd.DataFrame): 处理后的苹果股票和黄金ETF数据
    """
    # 读取原始数据（强制日期解析）
    df = pd.read_csv(filepath, parse_dates=['Date'])

    # 严格数据清洗流程
    for col in ['AAPL', 'GLD']:  # 遍历股票和黄金列
        # 1. 过滤非数字字符（正则表达式保留数字和小数点）
        df[col] = df[col].astype(str).str.replace('[^0-9.]', '', regex=True)
        
        # 2. 转换数值类型，无效值转为NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 3. 双重填充策略（先向前填充，后向后填充）
        df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        # 4. 极值处理（限制价格在0.01到1,000,000之间）
        df[col] = df[col].clip(lower=0.01, upper=1e6)

    # 数据切片与格式化
    aapl = df[['Date', 'AAPL']].set_index('Date').rename(columns={'AAPL': 'close'})  # 苹果数据
    gld = df[['Date', 'GLD']].set_index('Date').rename(columns={'GLD': 'close'})     # 黄金数据

    # 数据完整性验证
    assert not aapl['close'].isnull().any(), "AAPL数据存在无效值"
    assert not gld['close'].isnull().any(), "GLD数据存在无效值"

    return aapl, gld

# ================= 安全策略类 =================
class RobustDiversificationStrategy(bt.Strategy):
    """
    强化版分散策略类
    特征：
    - 双均线交易信号
    - 动态止损止盈
    - 仓位规模控制
    - 异常处理机制
    """
    # 策略参数组
    params = (
        ('ma_period', 20),         # 均线周期（20日）
        ('stop_loss', 0.05),       # 止损比例（5%）
        ('take_profit', 0.10),     # 止盈比例（10%）
        ('position_ratio', 0.45), # 单资产最大仓位比例（建议<0.5）
        ('min_trade_size', 1)      # 最小交易单位（1股/盎司）
    )

    def __init__(self):
        """初始化资产跟踪系统"""
        # 为每个资产创建跟踪字典
        self.assets = {
            data._name: {
                'sma': bt.indicators.SMA(data.close, period=self.params.ma_period),  # 均线指标
                'entry': None,    # 入场价格记录
                'last_price': None  # 最后有效价格缓存
            } for data in self.datas  # 遍历所有数据源（AAPL和GLD）
        }

        # 资金跟踪系统
        self.value_log = []  # 资金曲线记录
        
        # 定时器：每月初记录资金（用于绩效计算）
        self.add_timer(
            when=bt.timer.SESSION_END,  # 在交易日结束时触发
            monthdays=[1],              # 每月第1天
            monthcarry=True,            # 处理非交易日
            callback=self._record_value # 回调函数
        )

    def _record_value(self):
        """安全记录资金（防御NaN和异常值）"""
        val = self.broker.getvalue()  # 获取当前总资产
        
        # 有效性验证（过滤异常数值）
        if np.isfinite(val) and val > 0:
            self.value_log.append(val)
        else:
            print(f"警告：忽略无效资金记录: {val}")

    def next(self):
        """主交易逻辑（每个bar执行）"""
        # 遍历所有资产（AAPL和GLD）
        for data in self.datas:
            self._process_asset(data)

    def _process_asset(self, data):
        """处理单个资产的交易逻辑"""
        asset = self.assets[data._name]  # 获取资产跟踪信息
        pos = self.getposition(data)     # 当前持仓状态

        # 更新最后有效价格（防御零和NaN）
        if data.close[0] > 0 and not np.isnan(data.close[0]):
            asset['last_price'] = data.close[0]

        # 空仓时检查买入条件
        if not pos:
            self._check_buy(data, asset)
        # 持仓时检查卖出条件
        else:
            self._check_sell(data, asset)

    def _check_buy(self, data, asset):
        """执行买入条件检查（五重保护）"""
        # 条件1：数据长度足够计算均线
        # 条件2：价格上穿均线
        # 条件3：均线趋势向上
        if (
                len(data.close) > self.params.ma_period and
                data.close[0] > asset['sma'][0] and
                asset['sma'][0] > asset['sma'][-1]
        ):
            try:
                # 计算可用资金
                cash = self.broker.getcash()
                # 计算分配金额（总资金*仓位比例）
                alloc = cash * self.params.position_ratio
                # 获取当前价格
                price = data.close[0]

                # 五重安全验证
                if (price <= 0 or                        # 价格无效
                    np.isnan(price) or                   # 数值异常
                    alloc <= 0 or                        # 分配金额不足
                    cash <= 100 or                       # 保留最低现金（$100）
                    not np.isfinite(price)               # 非有限数值
                ):
                    return

                # 计算可买数量（取整且不低于最小交易单位）
                size = max(int(alloc / price), self.params.min_trade_size)
                
                # 执行买入
                if size > 0:
                    self.buy(data=data, size=size)
                    asset['entry'] = price  # 记录入场价格
                    print(f"{data.datetime.date()} {data._name} 买入 {size}股 @ {price:.2f}")
            except Exception as e:
                print(f"{data._name} 买入失败: {str(e)}")

    def _check_sell(self, data, asset):
        """执行卖出条件检查（含异常处理）"""
        # 异常持仓检测（入场价格为None时强制平仓）
        if asset['entry'] is None:
            print(f"{data.datetime.date()} {data._name} 发现异常持仓，强制平仓")
            self.close(data=data)
            return

        # 获取当前价格（使用最后有效价格作为后备）
        current_price = data.close[0] if data.close[0] > 0 else asset['last_price']
        
        # 计算止损止盈价格
        stop_price = asset['entry'] * (1 - self.params.stop_loss)
        profit_price = asset['entry'] * (1 + self.params.take_profit)

        # 触发止损/止盈条件
        if current_price < stop_price or current_price > profit_price:
            try:
                self.close(data=data)
                print(f"{data.datetime.date()} {data._name} 平仓 @ {current_price:.2f}")
            finally:
                asset['entry'] = None  # 重置入场价格（防止重复触发）

    def stop(self):
        """回测结束时计算绩效指标"""
        # 清理无效记录
        self.value_log = [x for x in self.value_log if np.isfinite(x)]
        
        # 计算关键指标
        if len(self.value_log) > 1:
            returns = pd.Series(self.value_log).pct_change().dropna()
            # 夏普比率（年化）
            sharpe = returns.mean() / returns.std() * np.sqrt(252)
            # 最大回撤
            max_drawdown = (pd.Series(self.value_log) / pd.Series(self.value_log).cummax() - 1).min()
        else:
            sharpe = np.nan
            max_drawdown = np.nan

        # 输出报告
        print(f"\n=== 最终绩效 ===")
        print(f"夏普比率: {sharpe:.2f}")
        print(f"最大回撤: {max_drawdown:.2%}")
        print(f"最终资金: {self.broker.getvalue():.2f}")

# ================= 执行回测 =================
if __name__ == '__main__':
    # 初始化回测引擎
    cerebro = bt.Cerebro()
    
    # 加载并处理数据
    aapl, gld = load_data('data/stock_gold_data.csv')

    # 构建AAPL数据源（补充完整OHLC结构）
    data_params = dict(
        dataname=pd.DataFrame({
            'open': aapl['close'],   # 使用收盘价模拟开盘价
            'high': aapl['close'],   # 使用收盘价模拟最高价
            'low': aapl['close'],    # 使用收盘价模拟最低价
            'close': aapl['close'],  # 收盘价
            'volume': 1000000        # 模拟成交量（100万股）
        }),
        name='AAPL'  # 资产名称
    )
    cerebro.adddata(bt.feeds.PandasData(**data_params))

    # 构建GLD数据源（同上）
    data_params['dataname'] = pd.DataFrame({
        'open': gld['close'],
        'high': gld['close'],
        'low': gld['close'],
        'close': gld['close'],
        'volume': 500000  # 模拟成交量（50万盎司）
    })
    data_params['name'] = 'GLD'
    cerebro.adddata(bt.feeds.PandasData(**data_params))

    # 配置回测参数
    cerebro.addstrategy(RobustDiversificationStrategy)  # 添加策略
    cerebro.broker.setcash(100000)                      # 初始资金10万美元
    cerebro.broker.setcommission(commission=0.001)      # 佣金率0.1%

    # 运行回测
    print('初始资金:', cerebro.broker.getvalue())
    cerebro.run()

    # 可视化（异常捕获防止崩溃）
    try:
        cerebro.plot(style='candlestick', volume=False)
    except Exception as e:
        print(f"警告：绘图功能跳过，原因: {str(e)}")