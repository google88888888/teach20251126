import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw


newDate='盟佳序202511.xlsx'
df=pd.read_excel(
    newDate,
    sheet_name='会计分录序时簿',
    usecols=['日期','凭证字号','摘要'],
    dtype={'日期':'str','凭证字号':'str','摘要':'str'}
)


print(df)
df=df.fillna(axis=0,method='ffill')
print(df)



# appNew = xw.App(visible=False)  # 不显示Excel界面
# wbNew = appNew.books.open('盟佳序202511.xlsx')
# wsNew = wbNew.sheets['会计分录序时簿']

# wbNew.save('盟佳序202511.xlsx')
# wbNew.close()
# appNew.quit()