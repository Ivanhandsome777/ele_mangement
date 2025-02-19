import logging
import threading
import datetime
import pandas as pd
import json
import os
import time
from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

# 全局变量
data_dict = {}
lock = threading.Lock()
last_data_time = None  # 记录第一个数据录入的时间
global users, df_ele

# 初始化日志
def init_logger():
    global asd,df_ele
    log_file_path = "log.txt"
    
    # 检查log.txt是否存在或为空
    if not os.path.exists(log_file_path) or os.path.getsize(log_file_path) == 0:
        asd = False
        # 创建空的log.txt文件
        with open(log_file_path, 'w') as f:
            pass
        
        # 创建空的DataFrame
        df_ele = pd.DataFrame(columns=['identifier', 'timestamp', 'usage'])
    else:
        # 读取log.txt文件并加载到DataFrame中
        df_ele = pd.read_csv(log_file_path, names=['identifier', 'timestamp', 'usage'],sep=',')
        asd = False
    return df_ele


def init_daily_csv():
    # 获取当前日期并格式化为指定字符串
    today = datetime.datetime.today()
    date_str = today.strftime("%Y.%m.%d")  # 例如: "2025.09.20"
    filename_date = date_str.replace(".", "_")  # 转换为"2025_09_20"
    filename = f"{filename_date}.csv"
    
    # 检查文件是否存在
    if not os.path.exists(filename):
        # 使用全局变量df_ele保存CSV
        global df_ele
        df_ele.to_csv(filename, index=False)

def write_log(identifier, timestamp, usage):
    """将 identifier, timestamp, usage 数据写入 log.txt 文件"""

    log_data = {
        'identifier': identifier,
        'timestamp': timestamp,
        'usage': usage
    }

    with open('log.txt', 'a') as f:
        f.write(json.dumps(log_data) + '\n')



