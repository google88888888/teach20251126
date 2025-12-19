import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw

dfReadOld = pd.read_excel(
    '鞋城序202510.xlsx', 
    sheet_name='会计分录序时簿',
    header=[0],
    usecols=['日期','凭证字号','摘要','科目代码', '科目名称', '借方金额', '贷方金额'],
    dtype={'日期' : str,'凭证字号' : str,'摘要' : str,'科目代码' : str,'科目名称' : str,'借方金额' : str,'贷方金额' : str},
)
dfReadNew = pd.read_excel(
    '鞋城序202511.xlsx', 
    sheet_name='会计分录序时簿',
    header=[0],
    usecols=['日期','凭证字号','摘要','科目代码', '科目名称', '借方金额', '贷方金额'],
    dtype={'日期' : str,'凭证字号' : str,'摘要' : str,'科目代码' : str,'科目名称' : str,'借方金额' : str,'贷方金额' : str},
)

appOld = xw.App(visible=False)  # 不显示Excel界面
wbOld = appOld.books.open('鞋城序202510.xlsx')
wsOld = wbOld.sheets[0]

appNew = xw.App(visible=False)  # 不显示Excel界面
wbNew = appNew.books.open('鞋城序202511.xlsx')
wsNew = wbNew.sheets[0]

oldList=dfReadOld.values.tolist()
newList=dfReadNew.values.tolist()

with open('oldList.json', 'w', encoding='utf-8') as f:
    json.dump(oldList, f, ensure_ascii=False, indent=4)
with open('newList.json', 'w', encoding='utf-8') as f:
    json.dump(newList, f, ensure_ascii=False, indent=4)

typeToColumn={
    '日期':0,
    '凭证字号':1,
    '摘要':2,
    '科目代码':3,
    '科目名称':4,
    '借方金额':5,
    '贷方金额':6,
}

for index,item in enumerate(oldList):
    hasDifferent=False
    if oldList[index][typeToColumn['日期']]!=newList[index][typeToColumn['日期']]:
        hasDifferent=True
        print('***日期'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['凭证字号']]!=newList[index][typeToColumn['凭证字号']]:
        hasDifferent=True
        print('***凭证字号'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['摘要']]!=newList[index][typeToColumn['摘要']]:
        hasDifferent=True
        print('***摘要'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['科目代码']]!=newList[index][typeToColumn['科目代码']]:
        hasDifferent=True
        print('***科目代码'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['科目名称']]!=newList[index][typeToColumn['科目名称']]:
        hasDifferent=True
        print('***科目名称'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['借方金额']]!=newList[index][typeToColumn['借方金额']]:
        hasDifferent=True
        print('***借方金额'+'——列的第——'+str(2+index)+'——行不相等***')

    if oldList[index][typeToColumn['贷方金额']]!=newList[index][typeToColumn['贷方金额']]:
        hasDifferent=True
        print('***贷方金额'+'——列的第——'+str(2+index)+'——行不相等***')

    if hasDifferent==False:
        realTypeToColumn={
            '自定义项目':12,
        }
        wsNew[1+index, realTypeToColumn['自定义项目']].value=wsOld[1+index, realTypeToColumn['自定义项目']].value
        print('第'+str(2+index)+'行相等')

wbOld.save('鞋城序202510.xlsx')
wbOld.close()
appOld.quit()

wbNew.save('鞋城序202511.xlsx')
wbNew.close()
appNew.quit()


