import random
import time
import logging
import sys
import os

# 创建logs目录（如果不存在）
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志记录
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 文件输出处理器，将日志输出到 logs/trading.log
file_handler = logging.FileHandler('logs/trading.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台输出处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 将文件处理器和控制台处理器都添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 模拟获取市场价格
def get_price(symbol):
    price = random.uniform(100, 200)  # 模拟价格波动
    logger.info(f"{symbol} 当前市场价格: {price:.2f} 元")
    return price

# 模拟买单操作
def buy(symbol, price, quantity):
    order_id = random.randint(1000, 9999)  # 模拟订单ID
    logger.info(f"买单已成功下单，{symbol} 买入 {quantity} 个，价格：{price:.2f} 元，订单ID: {order_id}")
    return order_id

# 模拟卖单操作
def sell(symbol, price, quantity):
    order_id = random.randint(1000, 9999)  # 模拟订单ID
    logger.info(f"卖单已成功下单，{symbol} 卖出 {quantity} 个，价格：{price:.2f} 元，订单ID: {order_id}")
    return order_id

# 配对交易策略实现
def generate_trading_signal(symbol1, symbol2, threshold):
    price1 = get_price(symbol1)
    price2 = get_price(symbol2)
    spread = price1 - price2
    
    if abs(spread) > threshold:
        return spread
    else:
        return None  # 未达到交易条件

# 风险管理：检查账户余额
def check_risk(account_balance, max_loss_percentage=0.02):
    if account_balance < max_loss_percentage:
        logger.warning("风险超过限制！停止所有交易。")
        return False  # 停止所有交易
    return True

# 配对交易策略的交易执行
def execute_pair_trading_strategy(symbol1, symbol2, threshold, account_balance):
    spread = generate_trading_signal(symbol1, symbol2, threshold)
    
    if spread:
        if spread > 0:
            buy(symbol2, get_price(symbol2), 10)  # 买入价差较低的资产
            sell(symbol1, get_price(symbol1), 10)  # 卖出价差较高的资产
            logger.info(f"执行配对交易：买入 {symbol2}，卖出 {symbol1}，价差：{spread:.2f}")
        else:
            sell(symbol2, get_price(symbol2), 10)  # 卖出价差较低的资产
            buy(symbol1, get_price(symbol1), 10)  # 买入价差较高的资产
            logger.info(f"执行配对交易：卖出 {symbol2}，买入 {symbol1}，价差：{spread:.2f}")
    else:
        logger.info(f"未满足交易条件：当前价差未超出阈值")
        
    time.sleep(1)

# 启动高频交易
def start_trading(symbols, threshold, account_balance):
    while True:
        if not check_risk(account_balance):
            break  # 风险超限，停止交易
        
        for symbol1 in symbols:
            for symbol2 in symbols:
                if symbol1 != symbol2:
                    execute_pair_trading_strategy(symbol1, symbol2, threshold, account_balance)
        
        time.sleep(1)  # 每秒执行一次

# 示例使用：监控AAPL、GOOGL和MSFT的价格变化，基于阈值执行策略
symbols = ["AAPL", "GOOGL", "MSFT"]
threshold = 5  # 配对交易阈值，超过5则执行交易
account_balance = 10000  # 初始账户余额

logger.info("启动模拟交易系统...")
start_trading(symbols, threshold, account_balance)  # 启动模拟交易
