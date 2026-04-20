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

dfReadMain = pd.read_excel(
    '银行存款.xlsx',
    sheet_name='银行存款',
    header=[0],
    dtype={'日期' : str,},
)

appMain = xw.App(visible=True)  # 不显示Excel界面
wbMain = appMain.books.open('银行存款.xlsx')
wsMainOfAll = wbMain.sheets['银行存款']
wsMainOfBorrow = wbMain.sheets['银行存款-借方']
wsMainOfLoan = wbMain.sheets['银行存款-贷方']

mainColumn={
    '日期凭证字凭证号':6,
    '一级科目':9,
    '借方金额':14,
    '贷方金额':15,
}

group={}
mainList=dfReadMain.values.tolist()
for mainIndex,mainItem in enumerate(mainList):
    if mainItem[mainColumn['日期凭证字凭证号']] in group:
        mainItem.append(mainIndex)
        group[mainItem[mainColumn['日期凭证字凭证号']]].append(mainItem)
    else:
        mainItem.append(mainIndex)
        group[mainItem[mainColumn['日期凭证字凭证号']]]=[mainItem]

with open('group.json', 'w', encoding='utf-8') as f:
    json.dump(group, f, ensure_ascii=False, indent=4)

indexOfBorrow=2
indexOfLoan=2
for key, value in group.items():
    belongToLoan=True
    for valueIndex,valueItem in enumerate(value):
        if valueItem[mainColumn['一级科目']]=='银行存款' and (not pd.isna(valueItem[mainColumn['借方金额']])):
            belongToLoan=False
            break
    if belongToLoan==True:
        for valueIndex,valueItem in enumerate(value):
            currentIndex=valueItem[len(valueItem)-1]+2
            data = wsMainOfAll.range(f"{currentIndex}:{currentIndex}").value
            wsMainOfLoan.range(f"{indexOfLoan}:{indexOfLoan}").value = data
            indexOfLoan=indexOfLoan+1
    else:
        for valueIndex,valueItem in enumerate(value):
            currentIndex=valueItem[len(valueItem)-1]+2
            data = wsMainOfAll.range(f"{currentIndex}:{currentIndex}").value
            wsMainOfBorrow.range(f"{indexOfBorrow}:{indexOfBorrow}").value = data
            indexOfBorrow=indexOfBorrow+1

wbMain.save('银行存款.xlsx')
wbMain.close()
appMain.quit()

