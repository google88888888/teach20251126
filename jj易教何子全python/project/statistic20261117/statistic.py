import os
import time
import hashlib
import shutil
from datetime import date, timedelta


BASE_NAME = "夜市早市合同台账"
CHECK_INTERVAL = 1  # 轮询间隔（秒）


def build_filename(day: date) -> str:
    # 根据日期生成台账文件名，如：./夜市早市合同台账2026-11-17.xlsx
    return f"./{BASE_NAME}{day.strftime('%Y-%m-%d')}.xlsx"


def prepare_today_file() -> str:
    """程序启动时检查今天的台账文件是否存在，若不存在则复制昨天的文档并重命名为今天的"""
    today = date.today()
    today_file = build_filename(today)

    if os.path.exists(today_file):
        print(f"今天的台账文件已存在:{today_file}")
        return today_file

    # 昨天的文档，如：./夜市早市合同台账2026-11-16.xlsx
    yesterday_file = build_filename(today - timedelta(days=1))
    if not os.path.exists(yesterday_file):
        print(f"找不到文件:{yesterday_file}，无法复制出今天的台账")
        return ""

    # 复制昨天的文档，并将文件名改成今天的
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


def main():
    # 程序启动时确保今天的台账文件存在（不存在则复制昨天的）
    file_path = prepare_today_file()
    if not file_path:
        return

    print(f"开始监听:{file_path}，按 Ctrl+C 退出")

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
            last_sig = current_sig


if __name__ == "__main__":
    main()
