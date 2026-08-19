import random
import time
import logging
import sys
import os

# 配置日志记录
log_dir = "logs"  # 自定义日志目录
if not os.path.exists(log_dir):  # 如果日志目录不存在，则创建
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'trading.log')

# 配置日志基本信息（文件日志）
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 创建控制台输出处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 获取日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 添加控制台和文件输出处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 模拟获取市场数据
def get_price(symbol):
    # 随机生成价格模拟市场波动
    price = random.uniform(140, 170)  # 随机生成价格，范围假设在140到170之间
    print(f"{symbol} 当前市场价格: {price:.2f} 元")
    logging.info(f"{symbol} 当前市场价格: {price:.2f} 元")  # 记录日志
    return price

# 模拟买单操作
def buy(symbol, price, quantity):
    print(f"下买单：买入 {quantity} 个 {symbol}，价格：{price:.2f} 元")
    logging.info(f"下买单：买入 {quantity} 个 {symbol}，价格：{price:.2f} 元")  # 记录日志
    order_id = random.randint(1000, 9999)  # 模拟订单ID
    logging.info(f"买单已成功下单，订单ID: {order_id}")  # 记录日志
    return order_id

# 模拟卖单操作
def sell(symbol, price, quantity):
    print(f"下卖单：卖出 {quantity} 个 {symbol}，价格：{price:.2f} 元")
    logging.info(f"下卖单：卖出 {quantity} 个 {symbol}，价格：{price:.2f} 元")  # 记录日志
    order_id = random.randint(1000, 9999)  # 模拟订单ID
    logging.info(f"卖单已成功下单，订单ID: {order_id}")  # 记录日志
    return order_id

# 模拟查询订单状态
def query_order(order_id):
    status = random.choice(["已成交", "待处理", "已撤销"])
    print(f"订单ID {order_id} 状态: {status}")
    logging.info(f"订单ID {order_id} 状态: {status}")  # 记录日志
    return status

# 模拟撤销订单
def cancel_order(order_id):
    print(f"撤销订单ID {order_id}...")
    logging.info(f"撤销订单ID {order_id}...")  # 记录日志
    print(f"订单ID {order_id} 已撤销。")
    logging.info(f"订单ID {order_id} 已撤销。")  # 记录日志

# 风险管理：检查账户余额和最大亏损限制
def check_risk(account_balance, max_loss_percentage=0.02):
    if account_balance < max_loss_percentage:
        print("风险超过限制！停止所有交易。")
        logging.warning("风险超过限制！停止所有交易。")  # 记录警告日志
        return False  # 停止所有交易
    return True

# 动量策略：根据价格变化进行决策
def momentum_strategy(symbol, threshold=0.5, last_price=None):
    price = get_price(symbol)
    
    # 如果是第一次获取价格，返回当前价格并不执行交易
    if last_price is None:
        return None, price

    # 计算价格变化百分比
    price_change = (price - last_price) / last_price
    
    # 判断是否符合动量策略：价格变化大于阈值时执行买入或卖出
    if price_change > threshold:
        return 'buy', price
    elif price_change < -threshold:
        return 'sell', price
    else:
        return None, price  # 不执行任何操作

# 交易策略执行：根据动量策略进行买卖
def execute_trading(symbol, threshold, account_balance, last_price):
    action, price = momentum_strategy(symbol, threshold, last_price)
    
    if action == 'buy' and check_risk(account_balance):
        # 执行买单操作
        buy(symbol, price, 10)  # 假设每次买入10股
    elif action == 'sell' and check_risk(account_balance):
        # 执行卖单操作
        sell(symbol, price, 10)  # 假设每次卖出10股

    return price  # 返回当前价格用于下一次判断

# 启动高频交易
def start_trading(symbol, threshold, account_balance):
    last_price = None
    
    while True:
        last_price = execute_trading(symbol, threshold, account_balance, last_price)
        time.sleep(1)  # 每秒执行一次交易策略

# 示例使用：监控AAPL股票价格变化，基于动量策略执行买卖
symbols = ["AAPL"]
threshold = 0.005  # 动量策略阈值，设定为价格变化超过0.5%则执行买卖
account_balance = 10000  # 初始账户余额

print("启动模拟高频交易系统...")
start_trading(symbols[0], threshold, account_balance)  # 启动AAPL的高频交易