import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw

dfReadMain = pd.read_excel(
    '鞋城2026.1月份租金).xlsx',
    sheet_name='2026.01',
    header=[0,1,2],
)
dfReadChild = pd.read_excel(
    '合同台账.xlsx', 
    sheet_name='2025.12.1',
    header=[0,1,2,3],
)


appMain = xw.App(visible=False)  # 不显示Excel界面
wbMain = appMain.books.open('鞋城2026.1月份租金).xlsx')
wsMain = wbMain.sheets[1]

mainColumn={
    '档口号':3,
    '面积':7,
    '租金':8,
}

childColumn={
    '档口号':2,
    '租金':16,
    '起租日':13,
    '到期日':14,
}

mainList=dfReadMain.values.tolist()
childList=dfReadChild.values.tolist()
# print(mainList)
# print(childList)

ts1 = pd.Timestamp('2026-01-01 00:00:00')
ts2 = pd.Timestamp('2026-01-31 23:59:59')

# print(ts1 <= ts2)  # True

for mainIndex,mainItem in enumerate(mainList):
    print(mainItem)
    if mainIndex<317:
        if pd.isna(mainItem[mainColumn['面积']]):
            print('没面积，不考虑',mainItem)
        elif pd.isna(mainItem[mainColumn['租金']]):
            print('有面积，没租金，从台账表去拿租金##################',mainItem)
            parts = str(mainItem[mainColumn['档口号']]).split('/')
            count=0
            needSetValue=False
            for childIndex,childItem in enumerate(childList):
                if (str(childItem[childColumn['档口号']]) in parts) and (not pd.isna(childItem[childColumn['租金']])) and (childItem[childColumn['起租日']]<=ts1) and (childItem[childColumn['到期日']]>=ts2):
                    needSetValue=True
                    count=count+float(childItem[childColumn['租金']])
            if needSetValue:
                wsMain[3+mainIndex, mainItem[mainColumn['租金']]].value=count


wbMain.save('鞋城2026.1月份租金).xlsx')
wbMain.close()
appMain.quit()



