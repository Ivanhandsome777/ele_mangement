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


# 写入日志文件
def write_log(data_to_log):
    with open('log.txt', 'a') as f:
        for item in data_to_log:
            f.write(json.dumps(item) + '\n')

# 清空数据字典
def clear_data_dict():
    global data_dict
    data_dict.clear()  # 无需在清空时加锁，因为此时已在process_data的锁内

# 处理数据并触发batchJob
def process_data():
    global data_dict,asd,last_data_time
    while True:
        if asd == False:  # 如果当前时间不在指定时间段内
            break  # 终止循环
        time.sleep(0.5)
        if data_dict:
            if len(data_dict) >= 100 or(last_data_time and now.timestamp() - last_data_time >= 1):
                with lock:
                    data_to_log = list(data_dict.values())
                    write_log(data_to_log)
                    clear_data_dict()
                    last_data_time = None
            elif last_data_time is None:
                last_data_time = now.timestamp()


# API接口 - 接收仪表数据
@app.route("/company/meter", methods=["POST"])
def meter_uploading():
    identifier = request.form.get("identifier")
    usage = request.form.get("usage")

    if identifier in users:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "identifier": identifier,
            "usage": usage,
            "timestamp": timestamp
        }
        data_dict[time.time()] = data
        return jsonify({'message': 'Data received'})
    else:
        return jsonify({'message': 'Invalid identifier'})




if __name__ == '__main__':
    init_logger()
    # 启动后台线程处理数据
    thread = threading.Thread(target=process_data)
    thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    thread.start()
    app.run(debug=True)

