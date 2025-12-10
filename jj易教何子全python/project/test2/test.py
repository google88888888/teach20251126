import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw
from pyecharts.charts import Bar
from pyecharts import options as opts

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

# 营业成本按考核
operatingCostBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 营业成本按非考核
operatingCostBaseOnNotAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 销售费用按考核
salesExpensesBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 销售费用按非考核
salesExpensesBaseOnNotAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 人员成本按考核
personnelCostsBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 人员成本按非考核
personnelCostsBaseOnNotAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 管理费用按考核
administrativeExpensesBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 管理费用按非考核
administrativeExpensesOnNotAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 财务费用按考核
financialExpensesBaseOnAssessment={
    'lastYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearPredictInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'thisYearRealInMonth':[0,0,0,0,0,0,0,0,0,0,0,0],
    'lastYearRealInQuarter':[0,0,0,0],
    'thisYearPredictInQuarter':[0,0,0,0],
    'thisYearRealInQuarter':[0,0,0,0],
}

# 财务费用按非考核
financialExpensesOnNotAssessment={
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

    # 营业成本按考核
    if(item[chineseToColumn['项目属性']]=='运营成本' and item[chineseToColumn['项目分类']]=='考核费用'):
        for i in range(12):
            operatingCostBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            operatingCostBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            operatingCostBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            operatingCostBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            operatingCostBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            operatingCostBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 营业成本按非考核
    if(item[chineseToColumn['项目属性']]=='运营成本' and item[chineseToColumn['项目分类']]=='非考核费用'):
        for i in range(12):
            operatingCostBaseOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            operatingCostBaseOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            operatingCostBaseOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            operatingCostBaseOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            operatingCostBaseOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            operatingCostBaseOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 销售费用按考核
    if(item[chineseToColumn['项目属性']]=='销售费用' and item[chineseToColumn['项目分类']]=='考核费用'):
        for i in range(12):
            salesExpensesBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            salesExpensesBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            salesExpensesBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            salesExpensesBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            salesExpensesBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            salesExpensesBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 销售费用按非考核
    if(item[chineseToColumn['项目属性']]=='销售费用' and item[chineseToColumn['项目分类']]=='非考核费用'):
        for i in range(12):
            salesExpensesBaseOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            salesExpensesBaseOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            salesExpensesBaseOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            salesExpensesBaseOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            salesExpensesBaseOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            salesExpensesBaseOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 人员成本按考核
    if(item[chineseToColumn['项目属性']]=='人员成本' and item[chineseToColumn['项目分类']]=='考核费用'):
        for i in range(12):
            personnelCostsBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            personnelCostsBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            personnelCostsBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            personnelCostsBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            personnelCostsBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            personnelCostsBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 人员成本按非考核
    if(item[chineseToColumn['项目属性']]=='人员成本' and item[chineseToColumn['项目分类']]=='非考核费用'):
        for i in range(12):
            personnelCostsBaseOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            personnelCostsBaseOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            personnelCostsBaseOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            personnelCostsBaseOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            personnelCostsBaseOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            personnelCostsBaseOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 管理费用按考核
    if(item[chineseToColumn['项目属性']]=='管理费用' and item[chineseToColumn['项目分类']]=='考核费用'):
        for i in range(12):
            administrativeExpensesBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            administrativeExpensesBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            administrativeExpensesBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            administrativeExpensesBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            administrativeExpensesBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            administrativeExpensesBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 管理费用按非考核
    if(item[chineseToColumn['项目属性']]=='管理费用' and item[chineseToColumn['项目分类']]=='非考核费用'):
        for i in range(12):
            administrativeExpensesOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            administrativeExpensesOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            administrativeExpensesOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            administrativeExpensesOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            administrativeExpensesOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            administrativeExpensesOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 财务费用按考核
    if(item[chineseToColumn['项目属性']]=='管理费用' and item[chineseToColumn['项目分类']]=='考核费用'):
        for i in range(12):
            financialExpensesBaseOnAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            financialExpensesBaseOnAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            financialExpensesBaseOnAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            financialExpensesBaseOnAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            financialExpensesBaseOnAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            financialExpensesBaseOnAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

    # 财务费用按非考核
    if(item[chineseToColumn['项目属性']]=='管理费用' and item[chineseToColumn['项目分类']]=='非考核费用'):
        for i in range(12):
            financialExpensesOnNotAssessment['lastYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3]
            financialExpensesOnNotAssessment['thisYearPredictInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+1]
            financialExpensesOnNotAssessment['thisYearRealInMonth'][i]+=item[chineseToColumn['1月去年实际数']+i*3+2]

        for i in range(4):
            financialExpensesOnNotAssessment['lastYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9]+item[chineseToColumn['1月去年实际数']+i*9+3]+item[chineseToColumn['1月去年实际数']+i*9+6]  
            financialExpensesOnNotAssessment['thisYearPredictInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+1]+item[chineseToColumn['1月去年实际数']+i*9+4]+item[chineseToColumn['1月去年实际数']+i*9+7] 
            financialExpensesOnNotAssessment['thisYearRealInQuarter'][i]+=item[chineseToColumn['1月去年实际数']+i*9+2]+item[chineseToColumn['1月去年实际数']+i*9+5]+item[chineseToColumn['1月去年实际数']+i*9+8]

with open('考核收入.json', 'w', encoding='utf-8') as f:
    json.dump(assessmentIncome, f, ensure_ascii=False, indent=2)

bar = Bar(init_opts=opts.InitOpts(width="100%", height="calc(100vh - 40px)"))
bar.add_xaxis(["1月", "2月", "3月", "4月", "5月", "6月","7月", "8月", "9月", "10月", "11月", "12月", ])
bar.add_yaxis("去年实际数", assessmentIncome['lastYearRealInMonth'])
bar.add_yaxis("本年实际数", assessmentIncome['thisYearRealInMonth'])
bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title="考核收入",
    ),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    # 图例会从series名称自动生成，不需要在LegendOpts中指定data
    legend_opts=opts.LegendOpts(),  # 空参数即可
    xaxis_opts=opts.AxisOpts(type_="category"),
    yaxis_opts=opts.AxisOpts(type_="value")
)
bar.render("考核收入—按月—去年实际数与本年实际数的对比.html")

bar = Bar(init_opts=opts.InitOpts(width="100%", height="calc(100vh - 40px)"))
bar.add_xaxis(["1季度", "2季度", "3季度", "4季度"])
bar.add_yaxis("去年实际数", assessmentIncome['lastYearRealInQuarter'])
bar.add_yaxis("本年实际数", assessmentIncome['thisYearRealInQuarter'])
bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title="考核收入",
    ),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    # 图例会从series名称自动生成，不需要在LegendOpts中指定data
    legend_opts=opts.LegendOpts(),  # 空参数即可
    xaxis_opts=opts.AxisOpts(type_="category"),
    yaxis_opts=opts.AxisOpts(type_="value")
)
bar.render("考核收入—季度—去年实际数与本年实际数的对比.html")



with open('营业收入按考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingRevenueBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('营业收入按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingRevenueBaseOnNotAssessment, f, ensure_ascii=False, indent=2)

with open('营业成本按考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingCostBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('营业成本按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(operatingCostBaseOnNotAssessment, f, ensure_ascii=False, indent=2)

with open('销售费用按考核.json', 'w', encoding='utf-8') as f:
    json.dump(salesExpensesBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('销售费用按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(salesExpensesBaseOnNotAssessment, f, ensure_ascii=False, indent=2)

with open('人员成本按考核.json', 'w', encoding='utf-8') as f:
    json.dump(personnelCostsBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('人员成本按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(personnelCostsBaseOnNotAssessment, f, ensure_ascii=False, indent=2)

with open('管理费用按考核.json', 'w', encoding='utf-8') as f:
    json.dump(administrativeExpensesBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('管理费用按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(administrativeExpensesOnNotAssessment, f, ensure_ascii=False, indent=2)

with open('财务费用按考核.json', 'w', encoding='utf-8') as f:
    json.dump(financialExpensesBaseOnAssessment, f, ensure_ascii=False, indent=2)

with open('财务费用按非考核.json', 'w', encoding='utf-8') as f:
    json.dump(financialExpensesOnNotAssessment, f, ensure_ascii=False, indent=2)