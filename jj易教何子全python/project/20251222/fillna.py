import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw


newDate='盟佳序202511.xlsx'
df=pd.read_excel(
    newDate,
    sheet_name='会计分录序时簿'
)
ffill_columns = ['日期','凭证字号','摘要']

df[ffill_columns] = df[ffill_columns].fillna(method='ffill')
df.to_excel(newDate, index=False)
