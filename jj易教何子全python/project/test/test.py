import pandas as pd
from datetime import datetime
# data = {
#     '员工ID': [1001, 1002, 1003, 1004, 1005],
#     '姓名': ['张三', '李四', '王五', '赵六', '钱七'],
#     '部门': ['技术部', '销售部', '技术部', '人事部', '销售部'],
#     '入职日期': ['2020-01-15', '2019-03-20', '2021-07-10', '2018-11-05', '2022-02-28'],
#     '基本工资': [8000, 6000, 8500, 5500, 6500],
#     '奖金': [2000, 3000, 2500, 1500, 2800],
#     '绩效评分': [85, 92, 78, 88, 95]
# }

# df = pd.DataFrame(data)
# df.to_excel('员工数据.xlsx', index=False, sheet_name='员工信息')

dfRead = pd.read_excel('员工数据.xlsx')
# print(dfRead)
# print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
# print(list(dfRead.columns))
# print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
# print(dfRead.values)
# print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
# print(dfRead.T.values)
# print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
originColums=list(dfRead.columns)
newList=dfRead.T.values.tolist()
a = [1006 ,'1' ,'2' ,'2023-04-05', 6 ,7 ,8]
for index,item in enumerate(newList):
    item.append(a[index])
    print(index,item)
newData={}
for index,item in enumerate(originColums):
    newData[item]=newList[index]
print(newData)


dfOut = pd.DataFrame(newData)
dfOut.to_excel('员工数据1.xlsx', index=False, sheet_name='员工信息')


