import pandas as pd
from datetime import datetime
import json
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import xlwings as xw
import shutil
import requests
import os

CACHE_FILE = "cache.json"

# 启动时加载缓存
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 保存缓存到文件
def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# 初始化缓存（全局）
cache = load_cache()

def fetch_data(url):

    if url in cache:
        print("走缓存")
        return cache[url]

    print("调用接口")
    headers={'Authorization': "您的token"}
    response = requests.get(url, headers=headers)

    cache[url] = response

    # 每次更新都写入文件（简单但安全）
    save_cache(cache)

    return response

res = fetch_data("http://open.api.tianyancha.com/services/v3/open/investtree?flag=4&dir=down&keyword=深圳市前海一方科技研发集团有限公司&minPercent=0&maxPercent=1")


investtree = json.loads(res["result"])

print(investtree)
