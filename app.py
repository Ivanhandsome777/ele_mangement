# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 21:56:20 2025

@author: 30048
"""

# Source: Geeksforgeeks

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for,render_template
import os
import csv
from datetime import datetime, timedelta
import os
from functions import calculate_usage,calculate_billing

app = Flask(__name__)

meter_readings = [
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 19, 0, 30), "reading_kwh": 144.5},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 18, 22, 0), "reading_kwh": 140},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 1, 18, 22, 30), "reading_kwh": 30},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 2, 12, 22, 30), "reading_kwh": 50},
    {"meter_id": "524-935-527", "timestamp": datetime(2025, 1, 1, 22, 30), "reading_kwh": 10},
]

LOG_FILE = 'meter_logs.txt'
# read user table and active machine list CSV everytime when initiate the process
# create empty user dictionary for user register, modity, and deactivate
admins = {} # {email address, password}
employees = {"admin@example.com": {"name": "Admin", "password": "password123"}}
# create empty user dictionary for user register, modity, and deactivate
users = {}  # { identifier: {address, region, sub_region, postcode, apartment_type} }
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

# save updated users profile to CSV when Flask is shut down
def save_data():
    with open("users.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["identifier", "address", "region", "sub_region", "postcode", "apartment_type"])
        writer.writeheader()
        for identifier, data in users.items():
            writer.writerow(data)

# initial main page of the website, and directly link to the /company/login page for company_side requests
@app.route("/", methods=["GET"])
def mainsite():
    return render_template('home.html')


@app.route("/User/query",methods=["GET","POST"])
def user_query():
    if request.method == 'POST':
        meter_id = request.form.get('meter_id')
        time_range = request.form.get('time_range')
        
        if not meter_id or not time_range:
            return render_template('user_query.html', error="please input all parameters needed")
            
        # 记录日志
        with open(LOG_FILE, 'a') as f:
            f.write(f"{datetime.now()}: 查询请求 - 电表ID: {meter_id}, 时间范围: {time_range}\n")
            
        return redirect(url_for('result', 
                             meter_id=meter_id,
                             time_range=time_range))
    
    return render_template('user_query.html')

@app.route('/User/query/result')
def result():
    meter_id = request.args.get('meter_id')
    time_range = request.args.get('time_range')
    
    usage = calculate_usage(meter_id, time_range)
    billing = calculate_billing(meter_id)
    
    if usage is None or billing is None:
        return render_template('user_query_result.html',
                             error="can not find data or insufficient data",
                             meter_id=meter_id)
    
    return render_template('user_query_result.html',
                         meter_id=meter_id,
                         time_range=time_range,
                         usage=usage,
                         billing=billing)

@app.route("/government",methods=["GET","POST"])
def government_analysis():

    pass

    return 

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        email = request.form.get("email")  # Use .get() to prevent KeyError
        password = request.form.get("password")

        # raise error if email is not found in admin reference table
        if email in admins and admins[email].get("password") == password:
            return redirect(url_for("company_main"))

        return render_template("company_login.html", message="Invalid credentials. Try again.")

    return render_template("company_login.html")


# main page after login, i.e. the dash board for company employee
@app.route("/company/main")
def company_main():
    return render_template('company_main.html')

# company register
@app.route("/company/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        identifier = request.form["identifier"]
        address = request.form["address"]
        region = request.form["region"]
        sub_region = request.form["sub_region"]
        postcode = request.form["postcode"]
        apartment_type = request.form["apartment_type"]

        # raise message if identifier already exist
        if identifier in users:
            return render_template("company_register.html", message="Identifier already exists! Try again.")

        # base on input message, create new user profile to memory
        users[identifier] = {
            "address": address,
            "region": region,
            "sub_region": sub_region,
            "postcode": postcode,
            "apartment_type": apartment_type
        }
        return render_template("company_register.html", message=f"New user {identifier} registered successfully!", success=True)
    # post the input data to the html webpage
    return render_template("company_register.html")

# modify currently existed users' profile
@app.route("/company/modify", methods=["GET", "POST"])
def modify_user():
    if request.method == "POST":
        identifier = request.form["identifier"]

        # raise error to notify that unavailable identifier input
        if identifier not in users:
            return render_template("company_modity.html", message = 'User not found! Try again')

        # update the user profile in system's memory and wait to be written to csv back-up after system shutting down
        users[identifier] = {
            "address": request.form["address"],
            "region": request.form["region"],
            "sub_region": request.form["sub_region"],
            "postcode": request.form["postcode"],
            "apartment_type": request.form["apartment_type"]
        }
        return render_template("company_modify.html", message = f"User {identifier} modified successfully!", success = True)

    return render_template("company_modify.html")

# deactivate a user's identifier
@app.route("/company/deactivate", methods=["GET", "POST"])
def deactivate_user():
    if request.method == "POST":
        identifier = request.form.get("identifier")

        # raise message to notify: user not found
        if identifier not in users:
            return render_template("company_deactivate.html", message = "User not found! Please try again")
        # if found user identifier, delete it from the memory table and update to csv system file after shutting
        del users[identifier]
        return render_template('company_deactivate.html', message = f"user {identifier} deleted successfully, wait for system udpate", success = True)

    return render_template('company_deactivate.html')

# quit the whole system (not finished yet)
@app.route("/company/quit")
def quit_app():
    pass

# initiate the app
if __name__ == '__main__':
    load_data() # load admin and users profile before initiating the app
    try:
        app.run(debug=False) # using debug = True will result in anaconda bugs, how to fix it?
    finally:
        save_data() # save changes on the users profile