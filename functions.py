import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import os

meter_readings = [
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 19, 0, 30), "reading_kwh": 144.5},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 18, 22, 0), "reading_kwh": 140},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 1, 18, 22, 30), "reading_kwh": 30},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 12, 22, 30), "reading_kwh": 50},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 1, 1, 22, 30), "reading_kwh": 10},
]

LOG_FILE = 'meter_logs.txt'

def calculate_usage(meter_id, time_range):
    # 获取目标电表的所有读数并按时间排序
    readings = sorted(
        [r for r in meter_readings if r['meter_id'] == meter_id],
        key=lambda x: x['timestamp']
    )
    if not readings:
        return None

    # 确定时间范围边界
    now = datetime.now()
    if time_range == 'last_half_hour':
        start_time = now - timedelta(minutes=30)
        end_time = now
    elif time_range == 'today':
        start_time = datetime(now.year, now.month, now.day)
        end_time = now
    elif time_range == 'week':
        start_time = now - timedelta(days=now.weekday())
        end_time = now
    elif time_range == 'month':
        start_time = datetime(now.year, now.month, 1)
        end_time = now
    elif time_range == 'last_month':
        end_time = (now.replace(day=1) - timedelta(days=1))
        start_time = end_time.replace(day=1)
    else:
        return None

    # 找到最接近时间范围边界的读数
    def find_closest(readings, target, mode):
        """
        mode: 'floor' (<= target) or 'ceil' (>= target)
        """
        candidates = []
        for r in readings:
            if mode == 'floor' and r['timestamp'] <= target:
                candidates.append(r)
            elif mode == 'ceil' and r['timestamp'] >= target:
                candidates.append(r)
        
        return max(candidates, key=lambda x: x['timestamp']) if candidates and mode == 'floor' \
               else min(candidates, key=lambda x: x['timestamp']) if candidates and mode == 'ceil' \
               else None

    # 获取边界读数
    start_reading = find_closest(readings, start_time, 'ceil')  # 第一个>=start_time的读数
    end_reading = find_closest(readings, end_time, 'floor')     # 最后一个<=end_time的读数

    if not start_reading or not end_reading:
        return None

    # 确保时间顺序有效
    if start_reading['timestamp'] > end_reading['timestamp']:
        return None

    return round(end_reading['reading_kwh'] - start_reading['reading_kwh'], 2)

def calculate_billing(meter_id):
    # 获取上月时间范围
    today = datetime.now()
    last_month_end = (today.replace(day=1) - timedelta(days=1))
    last_month_start = last_month_end.replace(day=1)
    
    # 获取相关读数
    readings = sorted(
        [r for r in meter_readings if r['meter_id'] == meter_id],
        key=lambda x: x['timestamp']
    )
    
    # 查找边界读数
    start_reading = next((r for r in readings if r['timestamp'] >= last_month_start), None)
    end_reading = next((r for r in reversed(readings) if r['timestamp'] <= last_month_end), None)
    
    if not start_reading or not end_reading:
        return None
    
    return round(end_reading['reading_kwh'] - start_reading['reading_kwh'], 2)import pandas as pd
import csv


class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf  
        self.keys = []  
        self.children = [] 

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)  
        self.t = t 

    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i][0]: 
            i += 1

        if i < len(node.keys) and key == node.keys[i][0]: 
            return node.keys[i][1] 

        if node.leaf: 
            return None
        
        return self.search(key, node.children[i])

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:  
            new_root = BTreeNode(False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root  
        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        """向非满节点插入 (id, value)"""
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i][0]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = (key, value)  
        else:
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:  
                self._split_child(node, i)
                if key > node.keys[i][0]: 
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, i):

        t = self.t
        full_child = parent.children[i]
        new_child = BTreeNode(full_child.leaf)

        parent.keys.insert(i, full_child.keys[t - 1]) 
        parent.children.insert(i + 1, new_child)

        new_child.keys = full_child.keys[t:]  
        full_child.keys = full_child.keys[:t - 1]  

        if not full_child.leaf:  
            new_child.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

    def traverse(self, node=None):
        if node is None:
            node = self.root

        for i in range(len(node.keys)):
            if not node.leaf:
                self.traverse(node.children[i])
            print(f"{node.keys[i][0]}: {node.keys[i][1]}", end="  ")

        if not node.leaf:
            self.traverse(node.children[-1])


def transform_to_BTree(column_name,df):
    if column_name == "id":
        df




