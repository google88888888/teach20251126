# -*- coding: utf-8 -*-
"""
监听当前文件夹下的《夜市 早市合同台账(1).xlsx》
文件被修改并保存后，打印 "文件已经被修改"

运行方式:  python watch_file.py
退出方式:  Ctrl + C
无需安装任何第三方库
"""
import os
import time
import hashlib

FILE_NAME = "夜市 早市合同台账(1).xlsx"
# 以脚本所在目录为基准拼出绝对路径，保证在任意位置启动都能找到文件
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)

CHECK_INTERVAL = 1  # 轮询间隔（秒）


def get_file_signature(path: str) -> tuple:
    """获取文件的指纹: (最后修改时间, 大小, 内容MD5)"""
    stat = os.stat(path)
    mtime = stat.st_mtime
    size = stat.st_size
    with open(path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    return mtime, size, md5


def main():
    if not os.path.exists(FILE_PATH):
        print(f"找不到文件: {FILE_PATH}")
        return

    print(f"开始监听: {FILE_PATH}")
    print("修改并保存 Excel 后会提示，按 Ctrl+C 退出...")

    last_sig = get_file_signature(FILE_PATH)

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            current_sig = get_file_signature(FILE_PATH)
        except (FileNotFoundError, PermissionError):
            # Excel 保存瞬间可能出现文件短暂占用/替换，跳过本次检查
            continue

        if current_sig != last_sig:
            print("文件已经被修改")
            last_sig = current_sig  # 更新基准，避免重复打印


if __name__ == "__main__":
    main()
