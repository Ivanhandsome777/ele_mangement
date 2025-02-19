import pandas as pd
import os
import csv
import threading
import queue
import logging
import json

# **Load CSV Data When Flask Starts**
def load_data():
    global admins, users
    # load data from admins.csv
    with open("admins.csv", "r") as file:
        reader = csv.DictReader(file)
        admins = {row["email"]: {"password": row["password"]} for row in reader}
    # load data from users.csv
    with open("users.csv", "r") as file:
        reader = csv.DictReader(file)
        users = {row["identifier"]: row for row in reader}
    print(admins)
    print(users)

# save updated users profile to CSV when Flask is shut down
def save_data():
    with open("users.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["identifier", "address", "region", "sub_region", "postcode", "apartment_type"])
        writer.writeheader()
        for identifier, data in users.items():
            writer.writerow(data)


