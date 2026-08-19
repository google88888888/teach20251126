CREATE TABLE account_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    transaction_date TEXT NOT NULL,                     -- 交易日期
    transaction_type TEXT NOT NULL,                     -- 交易类型
    amount DECIMAL(15, 2) NOT NULL,                     -- 交易金额
    balance DECIMAL(15, 2) NOT NULL                     -- 账户余额
);


-- 插入数据
INSERT INTO account_transactions (transaction_date, transaction_type, amount, balance)
VALUES ('2025-02-01', '存款', 5000.00, 10000.00),
       ('2025-02-02', '取款', 2000.00, 8000.00),
       ('2025-02-03', '存款', 3000.00, 11000.00),
       ('2025-02-04', '取款', 1000.00, 10000.00),
       ('2025-02-05', '存款', 1500.00, 11500.00);
