import argparse
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from openpyxl import load_workbook


def is_blank_row(row_values):
    return all(value is None or str(value).strip() == "" for value in row_values)


def format_value_for_doc(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    text = str(value).strip()
    if text == "":
        return ""
    try:
        num = float(text.replace(",", ""))
        return f"{num:,.2f}"
    except ValueError:
        return text


def set_paragraph_font(para):
    for run in para.runs:
        run.font.name = "宋体"
        run.font.size = Pt(10.5)
        rfonts = run._element.rPr.rFonts
        rfonts.set(qn("w:eastAsia"), "宋体")


def set_cell_font(cell):
    for para in cell.paragraphs:
        for run in para.runs:
            run.font.name = "宋体"
            run.font.size = Pt(10.5)
            rfonts = run._element.rPr.rFonts
            rfonts.set(qn("w:eastAsia"), "宋体")


def iter_doc_elements_from_title(doc, target_title):
    started = False
    for child in doc.element.body:
        if child.tag.endswith("p"):
            para = next((p for p in doc.paragraphs if p._element is child), None)
            if para is None:
                continue
            if not started and target_title in para.text:
                started = True
                yield "p", para
            elif started:
                yield "p", para
        elif started and child.tag.endswith("tbl"):
            table = next((t for t in doc.tables if t._element is child), None)
            if table is not None:
                yield "tbl", table


def load_excel_rows(excel_path):
    wb = load_workbook(excel_path, data_only=True)
    ws = wb.active
    return [tuple(row) for row in ws.iter_rows(values_only=True)]


def update_doc_from_excel(doc_path, excel_path, output_path, target_title):
    doc = Document(doc_path)
    excel_rows = load_excel_rows(excel_path)
    excel_index = 0

    def next_nonempty_row():
        nonlocal excel_index
        while excel_index < len(excel_rows) and is_blank_row(excel_rows[excel_index]):
            excel_index += 1
        if excel_index >= len(excel_rows):
            return None
        row = excel_rows[excel_index]
        excel_index += 1
        return row

    for elem_type, elem in iter_doc_elements_from_title(doc, target_title):
        if elem_type == "p":
            row = next_nonempty_row()
            if row is None:
                break
            value = row[0] if len(row) > 0 else None
            elem.text = format_value_for_doc(value)
            set_paragraph_font(elem)
        elif elem_type == "tbl":
            for table_row in elem.rows:
                row = next_nonempty_row()
                if row is None:
                    break
                for col_idx, cell in enumerate(table_row.cells):
                    cell.text = format_value_for_doc(row[col_idx] if col_idx < len(row) else None)
                    set_cell_font(cell)
            while excel_index < len(excel_rows) and is_blank_row(excel_rows[excel_index]):
                excel_index += 1

    doc.save(output_path)
    print(f"已保存回 Word：{output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将 Excel 中修改后的数据更新回 Word 文档。")
    parser.add_argument("--docx", default="./3、佑荣科技2025年财审报告附注.docx", help="要更新的 Word 文档路径")
    parser.add_argument("--excel", default="./附注_合并项目注释_完整格式1.xlsx", help="包含最新数据的 Excel 文件路径")
    parser.add_argument("--output", default=None, help="输出的 Word 文件路径。如果不指定则覆盖输入 docx")
    parser.add_argument("--title", default="八、财务报表主要项目注释", help="从该标题开始更新 Word 内容")
    args = parser.parse_args()

    output_file = args.output if args.output else args.docx
    update_doc_from_excel(Path(args.docx), Path(args.excel), Path(output_file), args.title)
