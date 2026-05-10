import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw
import shutil
import requests
import os
import openpyxl
from docx import Document
from collections import deque
from docx.shared import Pt
from docx.oxml.ns import qn
from pyecharts.charts import Bar
from pyecharts import options as opts
import time

# ========== 新增：记录开始时间 ==========
start_time = time.time()

# ========== 1. 读取原始数据（与原代码一致） ==========
dfReadMain = pd.read_excel(
    '银行存款1.xlsx', 
    sheet_name='银行存款',
    header=[0],
    dtype={'日期': str},
)

# ========== 2. 定义列位置（与原代码 mainColumn 完全一致） ==========
mainColumn = {
    '日期凭证字凭证号': 6,
    '一级科目': 9,
    '借方金额': 14,
    '贷方金额': 15
}

# 为每一行添加原始行索引（0-based，对应原代码中的 mainIndex）
dfReadMain['_mainIndex'] = range(len(dfReadMain))

# ========== 3. 构建 group 字典（与原逻辑完全一致） ==========
group = {}
mainList = dfReadMain.values.tolist()  # 包含 _mainIndex 列
for mainIndex, mainItem in enumerate(mainList):
    key = mainItem[mainColumn['日期凭证字凭证号']]
    # 原代码是在 group 中存储带 mainIndex 的行列表，这里保持一致
    row_with_index = mainItem.copy()
    row_with_index[-1] = mainIndex  # _mainIndex 列已在末尾
    if key in group:
        group[key].append(row_with_index)
    else:
        group[key] = [row_with_index]

# 保存 group.json（与原代码完全相同）
with open('group.json', 'w', encoding='utf-8') as f:
    json.dump(group, f, ensure_ascii=False, indent=4)

# ========== 4. 使用 pandas 批量筛选，替代 xlwings 逐行复制 ==========
# 准备两个列表，存放需要写入“借方”和“贷方”工作表的行数据（保持原始顺序）
borrow_rows = []
loan_rows = []

# 获取原始 DataFrame 的列名（不含辅助列）
original_columns = dfReadMain.columns[:-1]  # 去掉 _mainIndex

# 遍历每个分组（与原代码的 for key, value in group.items() 逻辑一致）
for key, value in group.items():
    # 判断该分组是否属于借方/贷方（逻辑与原代码完全一致）
    belong_to_loan = False
    belong_to_borrow = False
    for row_item in value:
        if row_item[mainColumn['一级科目']] == '银行存款' and not pd.isna(row_item[mainColumn['借方金额']]):
            belong_to_borrow = True
        if row_item[mainColumn['一级科目']] == '银行存款' and not pd.isna(row_item[mainColumn['贷方金额']]):
            belong_to_loan = True

    # 获取该分组中所有行在原始 DataFrame 中的位置（_mainIndex）
    indices = [row_item[-1] for row_item in value]  # 最后一个是 _mainIndex
    group_rows = dfReadMain.iloc[indices][original_columns]  # 取出原始行数据（不含辅助列）

    # 原代码中，只要分组满足条件，就复制整个分组的所有行（而不是只复制符合条件的行）
    if belong_to_loan:
        loan_rows.append(group_rows)
    if belong_to_borrow:
        borrow_rows.append(group_rows)

# 合并所有需要写入的行
if borrow_rows:
    df_borrow = pd.concat(borrow_rows, ignore_index=True)
else:
    df_borrow = pd.DataFrame(columns=original_columns)

if loan_rows:
    df_loan = pd.concat(loan_rows, ignore_index=True)
else:
    df_loan = pd.DataFrame(columns=original_columns)

# ========== 5. 写回 Excel 文件（覆盖原文件，但保留“银行存款”工作表） ==========
# 注意：原代码最后保存为 '银行存款1.xlsx'，并且只修改了该文件。
# 这里使用 pandas 批量写入，覆盖三个工作表。
with pd.ExcelWriter('银行存款1.xlsx', engine='openpyxl', mode='w') as writer:
    # 写入原始工作表“银行存款”（去掉辅助列 _mainIndex）
    dfReadMain[original_columns].to_excel(writer, sheet_name='银行存款', index=False)
    # 写入“银行存款-借方”
    df_borrow.to_excel(writer, sheet_name='银行存款-借方', index=False)
    # 写入“银行存款-贷方”
    df_loan.to_excel(writer, sheet_name='银行存款-贷方', index=False)

# ========== 新增：输出耗时 ==========
end_time = time.time()
print(f"处理完成，总耗时：{end_time - start_time:.2f} 秒")