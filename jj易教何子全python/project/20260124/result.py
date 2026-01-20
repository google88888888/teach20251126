import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw
import shutil

shutil.copy('合同台账.xlsx', '合同台账_1到12月统计.xlsx')
appChild = xw.App(visible=False)  # 不显示Excel界面
wbChild = appChild.books.open('合同台账_1到12月统计.xlsx')
wsChild = wbChild.sheets[0]
wsChild.name = f"{1}月"

for i in range(11):
    wsChild.copy(name=f"{i+2}月")  # 给新工作表命名

wbChild.save('合同台账_1到12月统计.xlsx')
wbChild.close()
appChild.quit()

childColumn={
    '档口号':2,
    '起租日':13,
    '到期日':14,
    '租金':16
}

has31=[1,3,5,7,8,10,12]
has30=[4,6,9,11]
current2Days=28

dfReadChild = pd.read_excel(
    '合同台账_1到12月统计.xlsx', 
    sheet_name='12月',
    header=[0,1,2,3],
)

dfChildList=dfReadChild.values.tolist()
appChild = xw.App(visible=False)  # 不显示Excel界面
wbChild = appChild.books.open('合同台账_1到12月统计.xlsx')
for currentMonthFrom0 in range(12):
    currentMonthFrom1=currentMonthFrom0+1
    endDay=current2Days
    if currentMonthFrom1 in has31:
        endDay=31
    elif currentMonthFrom1 in has30:
        endDay=30
    ts1 = pd.Timestamp(f'2026-{currentMonthFrom1}-01 00:00:00')
    ts2 = pd.Timestamp(f'2026-{currentMonthFrom1}-{endDay} 23:59:59')
    for childIndex,childItem in enumerate(dfChildList):
        if (not (ts2<childItem[childColumn['起租日']] or childItem[childColumn['到期日']]<ts1)) and (not pd.isna(childItem[childColumn['租金']])):
            print(f'这一行不用动，满足在租在{currentMonthFrom1}月且有租金',childItem,ts1,ts2,childItem[childColumn['到期日']],childItem[childColumn['起租日']],(childItem[childColumn['到期日']]>=ts1),(childItem[childColumn['起租日']]<=ts2))
        else:
            wsChild = wbChild.sheets[currentMonthFrom0]
            wsChild[4+childIndex, childColumn['租金']].value=0

wbChild.save('合同台账_1到12月统计.xlsx')
wbChild.close()
appChild.quit()


# dfReadMain = pd.read_excel(
#     '鞋城2026.1月份租金).xlsx', 
#     sheet_name='2026.01',
#     header=[0,1,2],
# )
# dfReadChild = pd.read_excel(
#     '合同台账.xlsx', 
#     sheet_name='2025.12.1',
#     header=[0,1,2,3],
# )

# appMain = xw.App(visible=False)  # 不显示Excel界面
# wbMain = appMain.books.open('鞋城2026.1月份租金).xlsx')
# wsMain = wbMain.sheets[1]



# dfMainList=dfReadMain.values.tolist()
# dfChildList=dfReadChild.values.tolist()



# mainColumn={
#     '档口号':5,
#     '面积':7,
#     '租金':8
# }

# childColumn={
#     '档口号':2,
#     '起租日':13,
#     '到期日':14,
#     '租金':16
# }

# ts1 = pd.Timestamp('2026-01-01 00:00:00')
# ts2 = pd.Timestamp('2026-01-31 23:59:59')

# for mainIndex,mainItem in enumerate(dfMainList):
#     if mainIndex<317:
#         if pd.isna(mainItem[mainColumn['面积']]):
#             print('没有面积，不考虑')
#         elif pd.isna(mainItem[mainColumn['租金']]):
#             print('有面积，没租金，到台账表找租金')
#             parts=str(mainItem[mainColumn['档口号']]).split('/')
#             count=0
#             needSetValue=False
#             for childIndex,childItem in enumerate(dfChildList):
#                 if (str(childItem[childColumn['档口号']]) in parts) and ((childItem[childColumn['到期日']]>=ts1) or (childItem[childColumn['起租日']]<=ts2)) and (not pd.isna(childItem[childColumn['租金']])):
#                     needSetValue=True
#                     count=count+float(childItem[childColumn['租金']])
#             if  needSetValue:
#                 wsMain[3+mainIndex, mainColumn['租金']].value=count

# wbMain.save('鞋城2026.1月份租金).xlsx')
# wbMain.close()
# appMain.quit()

# dfCountRate = pd.read_excel(
#     '鞋城2026.1月份租金).xlsx', 
#     sheet_name='2026.01',
#     header=[0,1,2],
# )

# dfCountRateList=dfCountRate.values.tolist()
# hasRentArea=0
# notHasRentArea=0

# floorValue={
#     '1':{
#         'hasRentArea':0,
#         'notHasRentArea':0
#     },
#     '2':{
#         'hasRentArea':0,
#         'notHasRentArea':0
#     },
#     '3':{
#         'hasRentArea':0,
#         'notHasRentArea':0
#     },
#     '4':{
#         'hasRentArea':0,
#         'notHasRentArea':0
#     },
#     '5':{
#         'hasRentArea':0,
#         'notHasRentArea':0
#     },
# }



# for countRateIndex,countRateValue in enumerate(dfCountRateList):
#     if(not pd.isna(countRateValue[mainColumn['面积']])) and countRateIndex<317:

#         mainColumnNumber=mainColumn['档口号']
#         mainColumnNumberValue=countRateValue[mainColumnNumber]
#         mainColumnNumberValueStr=str(mainColumnNumberValue)[0]
       
#         # print(mainColumnNumber,mainColumnNumberValue,mainColumnNumberValueStr,countRateValue,'aaaaaaaaaaaaaaaaaaaaaa')

#         if(pd.isna(countRateValue[mainColumn['租金']])):
#             notHasRentArea=notHasRentArea+countRateValue[mainColumn['面积']]
#             floorValue[mainColumnNumberValueStr]['notHasRentArea']=floorValue[mainColumnNumberValueStr]['notHasRentArea']+countRateValue[mainColumn['面积']]
#         else:
#             hasRentArea=hasRentArea+countRateValue[mainColumn['面积']]
#             floorValue[mainColumnNumberValueStr]['hasRentArea']=floorValue[mainColumnNumberValueStr]['hasRentArea']+countRateValue[mainColumn['面积']]
# # print('结果是：',hasRentArea/(hasRentArea+notHasRentArea))

# print('结果是1111111111111111：',floorValue)
# for key in floorValue:
#     if (floorValue[key]['hasRentArea']+floorValue[key]['notHasRentArea']) !=0:
#         print('第',key,'层的有租金面积除以总面积',floorValue[key]['hasRentArea']/(floorValue[key]['hasRentArea']+floorValue[key]['notHasRentArea']))
#     else:
#         print('第',key,'层的总面积为0')

            