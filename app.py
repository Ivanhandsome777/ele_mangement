# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 21:56:20 2025

@author: 30048
"""

# Source: Geeksforgeeks

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
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

# set up a virtual employee account
employees = {"admin@example.com": {"name": "Admin", "password": "password123"}}
# create empty user dictionary for user register, modity, and deactivate
users = {}  # { identifier: {address, region, sub_region, postcode, apartment_type} }

# initial main page of the website, and directly link to the /company/login page for company_side requests
@app.route("/", methods=["GET", "POST"])
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
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in employees and employees[email]["password"] == password:
            return redirect(url_for("main_menu"))
        else:
            return "<h1>Invalid credentials. <a href='/company/login'>Try again</a></h1>"

    return '''<h2>Company Employee Login</h2>
              <form method="POST">
                Email: <input type="text" name="email" required><br>
                Password: <input type="password" name="password" required><br>
                <button type="submit">Login</button>
              </form>'''

# main page after login, i.e. the dash board for company employee
@app.route("/company/main")
def main_menu():
    return '''<h2>Main Menu</h2>
              <ul>
                <li><a href="/company/register">Register a New User</a></li>
                <li><a href="/company/modify">Modify an Existing User</a></li>
                <li><a href="/company/deactivate">Deactivate a User</a></li>
                <li><a href="/company/quit">Quit</a></li>
              </ul>'''


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

        if identifier in users:
            return "<h1>Identifier already exists! <a href='/company/register'>Try again</a></h1>"

        users[identifier] = {
            "address": address,
            "region": region,
            "sub_region": sub_region,
            "postcode": postcode,
            "apartment_type": apartment_type
        }
        return f"<h1>New user {identifier} registered successfully! <a href='/company/main'>Go to Main Menu</a></h1>"
    # post the input data to the html webpage
    return '''<h2>Register New User</h2>
              <form method="POST">
                Identifier: <input type="text" name="identifier" required><br>
                Address: <input type="text" name="address" required><br>
                Region: <input type="text" name="region" required><br>
                Sub-Region: <input type="text" name="sub_region" required><br>
                Postcode: <input type="text" name="postcode" required><br>
                Apartment Type: <input type="text" name="apartment_type" required><br>
                <button type="submit">Register</button>
              </form>'''

# modify currently existed users' profile
@app.route("/company/modify", methods=["GET", "POST"])
def modify_user():
    if request.method == "POST":
        identifier = request.form["identifier"]

        if identifier not in users:
            return "<h1>User not found! <a href='/company/modify'>Try again</a></h1>"

        users[identifier] = {
            "address": request.form["address"],
            "region": request.form["region"],
            "sub_region": request.form["sub_region"],
            "postcode": request.form["postcode"],
            "apartment_type": request.form["apartment_type"]
        }
        return f"<h1>User {identifier} modified successfully! <a href='/company/main'>Go to Main Menu</a></h1>"

    return '''<h2>Modify Existing User</h2>
              <form method="POST">
                Identifier: <input type="text" name="identifier" required><br>
                New Address: <input type="text" name="address" required><br>
                New Region: <input type="text" name="region" required><br>
                New Sub-Region: <input type="text" name="sub_region" required><br>
                New Postcode: <input type="text" name="postcode" required><br>
                New Apartment Type: <input type="text" name="apartment_type" required><br>
                <button type="submit">Modify</button>
              </form>'''

# deactivate a user's identifier
@app.route("/company/deactivate", methods=["GET", "POST"])
def deactivate_user():
    if request.method == "POST":
        identifier = request.form["identifier"]

        if identifier not in users:
            return "<h1>User not found! <a href='/company/deactivate'>Try again</a></h1>"

        del users[identifier]
        return f"<h1>User {identifier} deactivated successfully! <a href='/company/main'>Go to Main Menu</a></h1>"

    return '''<h2>Deactivate User</h2>
              <form method="POST">
                Identifier: <input type="text" name="identifier" required><br>
                <button type="submit">Deactivate</button>
              </form>'''

# quit the whole system (not finished yet)
@app.route("/company/quit")
def quit_app():
    pass

# additional function: to write the updated users table and company employee table into a domestic file or store in some databse
pass

# initiate the app
if __name__ == '__main__':
    app.run(debug=False) # using debug = True will result in anaconda bugs, how to fix it?