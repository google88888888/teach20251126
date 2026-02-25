import openpyxl
from docx import Document

# 文件路径（请修改为实际路径）
excel_path = "1.xlsx"
word_path = "1.docx"

# 加载 Excel 工作簿
wb = openpyxl.load_workbook(excel_path, data_only=True)
sheet1 = wb.worksheets[0]  # 第一个 sheet
sheet2 = wb.worksheets[1]  # 第二个 sheet

# 加载 Word 文档
doc = Document(word_path)

# 获取文档中的所有表格
tables = doc.tables
if len(tables) < 2:
    raise Exception("Word 文档中至少需要两个表格")

table1 = tables[0]
table2 = tables[1]

# 填充第一个表格（假设 Excel 数据起始于 A1，即 row=1, col=1）
for i, row in enumerate(table1.rows):
    for j, cell in enumerate(row.cells):
        excel_value = sheet1.cell(row=i+1, column=j+1).value
        # 将值写入 Word 单元格，None 转为空字符串
        cell.text = str(excel_value) if excel_value is not None else ""

# 填充第二个表格
for i, row in enumerate(table2.rows):
    for j, cell in enumerate(row.cells):
        excel_value = sheet2.cell(row=i+1, column=j+1).value
        cell.text = str(excel_value) if excel_value is not None else ""

# 保存新文档（为避免覆盖原文件，建议另存为新文件）
doc.save("1.docx")
print("数据填充完成！")