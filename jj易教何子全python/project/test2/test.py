import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw

# 考核收入
assessmentIncome={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 营业收入按考核
operatingRevenueBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 营业收入按非考核
operatingRevenueBaseOnNotAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

chineseToColumn={
    '项目分类':2,
    '项目属性':3,
    '1月去年实际数':7,
    '1月今年预算数':8,
    '1月今年实际数':9,
    '2月去年实际数':10,
    '3月去年实际数':13,
    '4月去年实际数':16,
    '5月去年实际数':19,
    '6月去年实际数':22,
    '7月去年实际数':25,
    '8月去年实际数':28,
    '9月去年实际数':31,
    '10月去年实际数':34,
    '11月去年实际数':37,
    '12月去年实际数':40,
}

dfRead = pd.read_excel('工作簿1.xlsx', sheet_name='X项目',header=[0,1,2],skipfooter=2)
newList=dfRead.values.tolist()

for index,item in enumerate(newList):
    # 考核收入
    if(item[chineseToColumn['项目分类']]=='考核收入' and item[chineseToColumn['项目属性']]=='营业收入'):
        for i in range(12):
            assessmentIncome['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            assessmentIncome['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            assessmentIncome['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            assessmentIncome['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            assessmentIncome['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            assessmentIncome['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8] 

    if(item[chineseToColumn['项目分类']]=='考核收入' and item[chineseToColumn['项目属性']]=='运营成本'):
        for i in range(12):
            assessmentIncome['lastYearRealInMonth'][i]-=item[chineseToColumn['1月去年实际数']+i*3]
            assessmentIncome['thisYearPredictInMonth'][i]-=item[chineseToColumn['1月去年实际数']+i*3+1]
            assessmentIncome['thisYearRealInMonth'][i]-=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            assessmentIncome['lastYearRealInQuarter'][i]-=(item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6])
            assessmentIncome['thisYearPredictInQuarter'][i]-=(item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7])
            assessmentIncome['thisYearRealInQuarter'][i]-=(item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8])

    # 营业收入按考核
    if(item[chineseToColumn['项目属性']]=='营业收入' and item[chineseToColumn['项目分类']]=='考核收入'):
        for i in range(12):
            operatingRevenueBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            operatingRevenueBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            operatingRevenueBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            operatingRevenueBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            operatingRevenueBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            operatingRevenueBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 营业收入按非考核
    if(item[chineseToColumn['项目属性']]=='营业收入' and item[chineseToColumn['项目分类']]=='非考核收入'):
        for i in range(12):
            operatingRevenueBaseOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            operatingRevenueBaseOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            operatingRevenueBaseOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            operatingRevenueBaseOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            operatingRevenueBaseOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            operatingRevenueBaseOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

        
with open('考核收入.json', 'w', encoding='utf-8') as f:
    json.dump(assessmentIncome, f, ensure_ascii=False, indent=2)

with open('营业收入按考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingRevenueBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('营业收入按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingRevenueBaseOnNotAssessment, f, ensure_ascii=False, indent=2)

