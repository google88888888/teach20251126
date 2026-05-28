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
    # 构建包含工作表所有单元格值的矩阵（不使用 values_only 的迭代，以便按坐标填充合并单元格）
    max_row = ws.max_row
    max_col = ws.max_column
    grid = [[ws.cell(row=r, column=c).value for c in range(1, max_col + 1)] for r in range(1, max_row + 1)]

    # 展开所有合并单元格区域：将合并区域内每个格子都填充为主单元格（左上角）的值
    for mrange in ws.merged_cells.ranges:
        try:
            min_row, min_col, max_row_m, max_col_m = mrange.min_row, mrange.min_col, mrange.max_row, mrange.max_col
        except Exception:
            # 兼容老版本 openpyxl 的字符串表示
            bounds = mrange.bounds  # (min_col, min_row, max_col, max_row) in some versions
            min_col, min_row, max_col_m, max_row_m = bounds
        val = ws.cell(row=min_row, column=min_col).value
        for rr in range(min_row, max_row_m + 1):
            for cc in range(min_col, max_col_m + 1):
                grid[rr - 1][cc - 1] = val

    return [tuple(row) for row in grid]


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
    # 直接使用固定路径（如需修改请在此处更改）
    docx_path = Path("./3、佑荣科技2025年财审报告附注.docx")
    excel_path = Path("./附注_合并项目注释_完整格式1.xlsx")
    output_path = Path("./3、佑荣科技2025年财审报告附注_更新.docx")
    title = "八、财务报表主要项目注释"

    update_doc_from_excel(docx_path, excel_path, output_path, title)
