import pandas as pd
import datetime
import time
import threading
from logger import init_logger

def save_to_local(df_ele,filename,a,b):
    pass
    df_ele.to_csv(filename, index=False)

def merge_history():
    #将所有日期的数据合并，读取到内存
    df_merged=pd.Dataframe({})
    pass
    return df_merged

def recovery(df_merge,a,b): #通过a,b两个参数的传入，达成拆分任务的目的
    query_tree=[]
    pass
    return query_tree


def csv_job(filename,a,b):
    #任务1：先把log存了
    global df_ele #现在df_ele有了数据（因为前一流程）
    save_to_local(df_ele,filename,a,b)

    #任务2：recover
    global trees,df_merged
    tree=recovery(df_merged,a,b)
    trees.append(tree)

    time.sleep(b*0.1)
    print(f"job {a} exiting time taken {b*0.1} sec")

# def log_job(no, dur):
#     print(f"job {no} starting, will complete in {dur} sec")
#     time.sleep(dur)
#     print(f"job {no} exiting time taken {dur} sec")


def batchJobs():
    today = datetime.datetime.today()
    date_str = today.strftime("%Y.%m.%d")  # 例如: "2025.09.20"
    filename_date = date_str.replace(".", "_")  # 转换为"2025_09_20"
    filename = f"{filename_date}.csv"

    global trees
    trees=[]
    merge_history() #准备好第二个工作的数据

    threads=[]
    for a in range(10):
        for b in range(3):
            t=threading.Thread(target=csv_job, args=(filename,a,b))
            threads.append(t)
            t.start()
    for each in threads:
        each.join()