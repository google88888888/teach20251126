import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw
import shutil

dfReadLeft = pd.read_excel(
    '121 销售大表-2025.xlsx', 
    sheet_name='南京-2025-销售',
    header=[0,1,2,3],
)
dfReadLeftList=dfReadLeft.values.tolist()
with open('dfReadLeftList.json', 'w', encoding='utf-8') as f:
    json.dump(dfReadLeftList, f, ensure_ascii=False, indent=4)

dfReadRight = pd.read_excel(
    '121 销售大表-2025.xlsx', 
    sheet_name='25年收入凭证',
    header=[0,1,2,3],
)
dfReadRightList=dfReadRight.values.tolist()
with open('dfReadRightList.json', 'w', encoding='utf-8') as f:
    json.dump(dfReadRightList, f, ensure_ascii=False, indent=4)

typeToColumnOfLeft={
    '单据编号':3,
    '金额':19,
    '凭证唯一码(未开票)':39,
    '凭证合并(未开票)':40,
    '凭证金额(未开票)':41,
    '凭证唯一码(已开票)':44,
    '凭证合并(已开票)':45,
    '凭证金额(已开票)':46,
}
leftResult={}
for index,item in enumerate(dfReadLeftList):
    currentOrderNumber=item[typeToColumnOfLeft['单据编号']]
    if currentOrderNumber not in leftResult:
        leftResult[currentOrderNumber]={
            'amount':0,
            'isna':True,
            'indexAll':[],
        }
    if (not pd.isna(item[typeToColumnOfLeft['金额']])):
        leftResult[currentOrderNumber]['amount']=leftResult[currentOrderNumber]['amount']+item[typeToColumnOfLeft['金额']]
        leftResult[currentOrderNumber]['isna']=False
    leftResult[currentOrderNumber]['indexAll'].append(index)

with open('leftResult.json', 'w', encoding='utf-8') as f:
    json.dump(leftResult, f, ensure_ascii=False, indent=4)



def find_first_containing(lst, substring="XSCKD"):
    for item in lst:
        if substring in str(item):  # 确保将非字符串项转换为字符串
            return item
    return ''  # 未找到时返回 None
typeToColumnOfRight={
    '摘要':3,
    '贷方金额':8,
    '科目全名':5,
    '凭证唯一码':0,
    '凭证合并':2,
    '凭证金额':8,
}
rightResult={}
for index,item in enumerate(dfReadRightList):
    splitArray=str(item[typeToColumnOfRight['摘要']]).split('/')
    currentOrderNumber=find_first_containing(splitArray)
    if currentOrderNumber !='':
        if currentOrderNumber not in rightResult :
            rightResult[currentOrderNumber]={
                'amount':0,
                'isna':True,
                'indexAll':[],
            }
        if (not pd.isna(item[typeToColumnOfRight['贷方金额']])):
            rightResult[currentOrderNumber]['amount']=rightResult[currentOrderNumber]['amount']+item[typeToColumnOfRight['贷方金额']]
            rightResult[currentOrderNumber]['isna']=False
        rightResult[currentOrderNumber]['indexAll'].append(index)

with open('rightResult.json', 'w', encoding='utf-8') as f:
    json.dump(rightResult, f, ensure_ascii=False, indent=4)

appMain = xw.App(visible=True)  # 不显示Excel界面
wbMain = appMain.books.open('121 销售大表-2025.xlsx')
wsMain = wbMain.sheets[0]
needAddLineAfter=[]
for key, value in leftResult.items():
    if key in rightResult:
        if (not leftResult[key].isna) and (not rightResult[key].isna) and (leftResult[key].amount==rightResult[key].amount):
            if len(leftResult[key]['indexAll'])!=len(rightResult[key]['indexAll']):
                print(key,'编号的左右条目数量对不上，请人工查看')
            for index,item in enumerate(leftResult[key]['indexAll']):
                if index<len(rightResult[key]['indexAll']):
                    if '已开票' in str(rightResult[index][typeToColumnOfRight['科目全名']]):
                        wsMain[4+index,typeToColumnOfLeft['凭证唯一码(已开票)']].value=rightResult[index][typeToColumnOfRight['凭证唯一码']]
                        wsMain[4+index,typeToColumnOfLeft['凭证合并(已开票)']].value=rightResult[index][typeToColumnOfRight['凭证合并']]
                        wsMain[4+index,typeToColumnOfLeft['凭证金额(已开票)']].value=rightResult[index][typeToColumnOfRight['凭证金额']]
                    else:
                        wsMain[4+index,typeToColumnOfLeft['凭证唯一码(未开票)']].value=rightResult[index][typeToColumnOfRight['凭证唯一码']]
                        wsMain[4+index,typeToColumnOfLeft['凭证合并(未开票)']].value=rightResult[index][typeToColumnOfRight['凭证合并']]
                        wsMain[4+index,typeToColumnOfLeft['凭证金额(未开票)']].value=rightResult[index][typeToColumnOfRight['凭证金额']] 
        else:
            needAddLineAfter.append(leftResult[key]['indexAll'][-1])   
    else:
        needAddLineAfter.append(leftResult[key]['indexAll'][-1])

needAddLineAfterSort=sorted(needAddLineAfter, reverse=True)


wbMain.save('121 销售大表-2025.xlsx')
wbMain.close()
appMain.quit()


# appMain = xw.App(visible=True)  # 不显示Excel界面
# wbMain = appMain.books.open('123.xlsx')
# wsMain = wbMain.sheets[0]

# row_number = 13
# wsMain.range(f'{row_number}:{row_number}').insert(shift='down')

# wbMain.save('123.xlsx')
# wbMain.close()
# appMain.quit()