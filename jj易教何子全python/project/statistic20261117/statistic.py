import os
import time
import hashlib
import shutil
from datetime import datetime,date, timedelta
from openpyxl import load_workbook

BASE_NAME = "夜市早市合同台账"
CHECK_INTERVAL = 1  # 轮询间隔（秒）

# 根据日期生成台账文件名，如：./夜市早市合同台账2026-11-17.xlsx
def build_filename(day: date) -> str:
    # 把日期对象格式化成字符串：
    # %Y：四位年份，如 2026
    # %m：两位月份，如 11
    # %d：两位日期，如 17
    return f"./{BASE_NAME}{day.strftime('%Y-%m-%d')}.xlsx"

# 程序启动时检查今天的台账文件是否存在，若不存在则复制昨天的台账文件并重命名为今天的
def prepare_today_file() -> str:

    today = date.today()
    today_file = build_filename(today)
    if os.path.exists(today_file):
        print(f"今天的台账文件已存在:{today_file}")
        return today_file

    # 昨天的台账文件名，如：./夜市早市合同台账2026-11-16.xlsx
    # timedelta(days=1)为1天的时间间隔
    yesterday_file = build_filename(today - timedelta(days=1))
    if not os.path.exists(yesterday_file):
        print(f"找不到文件:{yesterday_file}，无法复制出今天的台账")
        return ""

    # 复制昨天的台账文件，并将文件名改成今天的
    # shutil 是 Python 标准库中的一个模块，名字来自 shell utilities，主要用来做文件和目录的高级操作。比 os 模块更方便
    # shutil.copy2 在复制文件内容的同时，还会保留文件的元数据，如：
    #     修改时间
    #     访问时间
    #     文件权限等
    # shutil.copy 只复制文件内容和权限，不会保留文件的元数据。
    shutil.copy2(yesterday_file, today_file)
    print(f"已复制{yesterday_file}并重命名为{today_file}")
    return today_file


def get_file_signature(path: str) -> tuple:
    stat = os.stat(path)
    # 获取文件最后修改时间
    mtime = stat.st_mtime
    # 获取文件大小
    size = stat.st_size
    # 以只读（read）模式，二进制（binary）模式，返回bytes
    with open(path, "rb") as f:
        # 获取文件的bytes
        readBinaryBytes=f.read()
        # 获取 MD5 摘要
        md5Origin = hashlib.md5(readBinaryBytes)
        # 将 MD5 摘要转成 32 个字符的十六进制字符串
        md5Hex=md5Origin.hexdigest()
    return mtime, size, md5Hex

columnNotNeedClear={
    '序号':1,
    '基本区域':2,
    '摊号':3,
    '方案_租金':4,
}
columnNeedClear={
    '档主名':5,
    '空档':6,
    '备注':7,
    '连档说明':8,
    '经营项目':9,
    '签约日':10,
    '起租日':11,
    '到期日':12,
    '月份':13,
    '保证金':14,
    '管理费':15,
    '档主身份证':16,
    '档主联系电话':17,
    '押金收费日期':18,
    '押金收款方式_民生':19,
    '押金收款方式_现金':20,
    '押金收款方式_李文州':21,
    '押金收款方式_陈龙炎':22,
    '押金收款方式_合计':23,
    '租金收费日期':24,
    '租金收款方式_民生':25,
    '租金收款方式_现金':26,
    '租金收款方式_李文州':27,
    '租金收款方式_陈龙炎':28,
    '租金收款方式_合计':29,
    '未交合计':30,
}

def clear_file(file_path):
    wbChild = load_workbook(file_path)
    wsChild = wbChild.worksheets[0]

    last_row = wsChild.max_row
    last_col = wsChild.max_column

    for rowIndexFrom1 in range(3,last_row+1):
        target=wsChild.cell(row=rowIndexFrom1, column=columnNeedClear['到期日']).value
        if target:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if target < today:
                for k, v in columnNeedClear.items():
                    wsChild.cell(row=rowIndexFrom1, column=v).value=None

    wbChild.save(file_path)
    wbChild.close()


def collectInformation(file_path):
    wbChild = load_workbook(file_path)
    wsChild = wbChild.worksheets[0]

    last_row = wsChild.max_row
    last_col = wsChild.max_column

    for rowIndexFrom1 in range(3,last_row+1):
        area=wsChild.cell(row=rowIndexFrom1, column=columnNotNeedClear['基本区域']).value
        stallNumber=wsChild.cell(row=rowIndexFrom1, column=columnNotNeedClear['摊号']).value
        name=wsChild.cell(row=rowIndexFrom1, column=columnNeedClear['档主名']).value
        id=wsChild.cell(row=rowIndexFrom1, column=columnNeedClear['档主身份证']).value
        phone=wsChild.cell(row=rowIndexFrom1, column=columnNeedClear['档主联系电话']).value
        if name and not id:
            print(f'基本区域：{area} 摊号：{stallNumber} 的 {name} 需要核实档主身份证')
        if name and not phone:
            print(f'基本区域：{area} 摊号：{stallNumber} 的 {name} 需要核实档主联系电话')
        # target=wsChild.cell(row=rowIndexFrom1, column=columnNeedClear['到期日']).value
            

    wbChild.save(file_path)
    wbChild.close()

def main():
    file_path = prepare_today_file()
    if not file_path:
        return

    clear_file(file_path)

    print(f"开始监听:{file_path}，按 Ctrl+C 退出")

    collectInformation(file_path)
    last_sig = get_file_signature(file_path)

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            current_sig = get_file_signature(file_path)
        except (FileNotFoundError, PermissionError):
            # Excel保存瞬间可能出现文件短暂占用/替换，跳过本次检查
            continue

        if current_sig != last_sig:
            print("文件已经被修改")
            collectInformation(file_path)
            last_sig = current_sig


if __name__ == "__main__":
    main()

