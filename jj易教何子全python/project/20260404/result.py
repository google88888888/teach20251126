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

date='2026-01-11'
dateTimestamp = pd.Timestamp(date)

dfReadMain = pd.read_excel(
    '1.xlsx',
    sheet_name='国大广场',
    header=[0],
)

mainColumn={
    '合同出租面积':3,
    '合同起租日':10,
    '合同到期日':11,
}

print(dateTimestamp)
hasRentArea=0
notHasRentArea=0

mainList=dfReadMain.values.tolist()
for mainIndex,mainItem in enumerate(mainList):
    if (not pd.isna(mainItem[mainColumn['合同出租面积']])):
        if (not pd.isna(mainItem[mainColumn['合同起租日']])) and (not pd.isna(mainItem[mainColumn['合同到期日']])) and (mainItem[mainColumn['合同起租日']]<=dateTimestamp) and (dateTimestamp<=mainItem[mainColumn['合同到期日']]):
            print('正在租',mainIndex,mainItem)
            hasRentArea=hasRentArea+mainItem[mainColumn['合同出租面积']]
        else:
            print('没在租',mainIndex,mainItem)
            notHasRentArea=notHasRentArea+mainItem[mainColumn['合同出租面积']]

allRentArea=hasRentArea+notHasRentArea
allRentArea=round(allRentArea,2)
hasRentArea=round(hasRentArea,2)
notHasRentArea=round(notHasRentArea,2)

print(allRentArea,hasRentArea,notHasRentArea)

title=f"{date}，国大广场可出租面积总数为{allRentArea}，已出租面积为{hasRentArea}，未出租面积为{notHasRentArea}，出租率为{hasRentArea/allRentArea*100:.2f}%"

bar = Bar(init_opts=opts.InitOpts(width="100%", height="calc(100vh - 40px)"))
bar.add_xaxis(["可出租面积总数", "已出租面积", "未出租面积"])
bar.add_yaxis(date, [allRentArea,hasRentArea,notHasRentArea])
bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title=title,
    ),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    # 图例会从series名称自动生成，不需要在LegendOpts中指定data
    legend_opts=opts.LegendOpts(),  # 空参数即可
    xaxis_opts=opts.AxisOpts(type_="category"),
    yaxis_opts=opts.AxisOpts(type_="value")
)
bar.render(f"{title}.html")
