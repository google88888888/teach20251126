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
    '楼层':1,
    '档口号':2,
    '面积':4,
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


dfCountRate = pd.read_excel(
    '合同台账_1到12月统计.xlsx', 
    sheet_name=None,
    header=[0,1,2,3],
)
for sheet_name, df in dfCountRate.items():
    print(f"\n工作表: {sheet_name}")
    dfCountRateList=df.values.tolist()

    floorValue={
        '一':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
        '二':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
        '三':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
        '四':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
        '五':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
        '总体':{
            'hasRentArea':0,
            'notHasRentArea':0,
            'totalArea':0,
            'rate':0,
        },
    }
    for countRateIndex,countRateValue in enumerate(dfCountRateList):
        if(not pd.isna(countRateValue[childColumn['楼层']])) and (not pd.isna(countRateValue[childColumn['面积']])):

            mainColumnNumber=childColumn['楼层']
            mainColumnNumberValue=countRateValue[mainColumnNumber]
            mainColumnNumberValueStr=str(mainColumnNumberValue)[0]
        
            if(countRateValue[childColumn['租金']]==0):
                floorValue['总体']['notHasRentArea']=floorValue['总体']['notHasRentArea']+countRateValue[childColumn['面积']]
                floorValue[mainColumnNumberValueStr]['notHasRentArea']=floorValue[mainColumnNumberValueStr]['notHasRentArea']+countRateValue[childColumn['面积']]

                floorValue['总体']['totalArea']=floorValue['总体']['totalArea']+countRateValue[childColumn['面积']]
                floorValue[mainColumnNumberValueStr]['totalArea']=floorValue[mainColumnNumberValueStr]['totalArea']+countRateValue[childColumn['面积']]
            else:
                floorValue['总体']['hasRentArea']=floorValue['总体']['hasRentArea']+countRateValue[childColumn['面积']]
                floorValue[mainColumnNumberValueStr]['hasRentArea']=floorValue[mainColumnNumberValueStr]['hasRentArea']+countRateValue[childColumn['面积']]

                floorValue['总体']['totalArea']=floorValue['总体']['totalArea']+countRateValue[childColumn['面积']]
                floorValue[mainColumnNumberValueStr]['totalArea']=floorValue[mainColumnNumberValueStr]['totalArea']+countRateValue[childColumn['面积']]

    for key in floorValue:
        if floorValue[key]['totalArea']!=0:
            floorValue[key]['rate']=floorValue[key]['hasRentArea']/floorValue[key]['totalArea']
    with open(f'{sheet_name}统计.json', 'w', encoding='utf-8') as f:
        json.dump(floorValue, f, ensure_ascii=False, indent=4)


