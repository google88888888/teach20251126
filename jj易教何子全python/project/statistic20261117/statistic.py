import os
import time
import hashlib


FILE_PATH = "./夜市早市合同台账2026-11-16.xlsx"
CHECK_INTERVAL = 1  # 轮询间隔（秒）


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
    if not os.path.exists(FILE_PATH):
        print(f"找不到文件:{FILE_PATH}")
        return

    print(f"开始监听:{FILE_PATH}，按 Ctrl+C 退出")

    last_sig = get_file_signature(FILE_PATH)

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            current_sig = get_file_signature(FILE_PATH)
        except (FileNotFoundError, PermissionError):
            # Excel保存瞬间可能出现文件短暂占用/替换，跳过本次检查
            continue

        if current_sig != last_sig:
            print("文件已经被修改")
            last_sig = current_sig


if __name__ == "__main__":
    main()
