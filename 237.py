import os
import csv
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request, redirect, url_for, render_template
import threading
import threading
import time
import random

from jobs import batchJobs
from functions import load_data,save_data
from logger import init_logger,init_daily_csv,write_log

acceptAPI = True
app = Flask(__name__)

# ===========================================================
# 初始化的逻辑都写在这里

global asd #accidental shutdown
global df_ele,log_lock
init_logger() # 启动后台线程处理数据：这里会先检查log如果存在，说明之前意外掉线
init_daily_csv()
log_lock = threading.Lock()
# thread = threading.Thread(target=process_data)
# thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
# thread.start()

# ===========================================================

@app.route("/", methods=["GET"])
def mainsite():
    if acceptAPI:
        return(render_template('home.html'))
    else:
        return(render_template('api_shutdown.html'))



@app.route("/user",methods=["GET","POST"])
def user_query():
    return(render_template('user_login.html'))


@app.route("/government",methods=["GET","POST"])
def government_analysis():

    pass

    return 

# read user table and active machine list CSV everytime when initiate the process
## 1. create empty user dictionary for user register, modity, and deactivate
admins = {} # {email address, password}
employees = {"admin@example.com": {"name": "Admin", "password": "password123"}}

## 2. create empty user dictionary for user register, modity, and deactivate
users = {}  # { identifier: {address, region, sub_region, postcode, apartment_type} }
print(users)



# ===========================================================
# 粘贴其他route入口

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
@app.route("/company/main", methods=["GET", "POST"])
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
    
    save_data() # save changes on the users profile
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

# ===========================================================

# upload meter electricity usage
@app.route("/company/meter", methods=["GET", "POST"])
def meter_uploading():
    global df_ele
    global log_lock
    if request.method == "POST":
        identifier = request.form.get("identifier")
        usage = request.form.get("usage")

        if identifier in users:
            # Append to DataFrame
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # 【Dataframe】
            new_row = {'identifier': identifier, 'usage': usage, 'timestamp': timestamp}
            df_ele.loc[len(df_ele)] = new_row

            # 【Log】Append to log.txt (comma-separated)
            with log_lock:  # get the lock
                try:
                    write_log(identifier, timestamp, usage)
                    return redirect(url_for("meter_uploaded", identifier=identifier, usage=usage))  #succeeded
                except Exception as e:
                    return jsonify({'message': 'Data uploading failed.'})  #failed
        else:
            return render_template("meter_upload.html", message="Invalid credentials. Try again.")

    return render_template("meter_upload.html")

@app.route("/company/meter_uploaded")
def meter_uploaded():
    identifier = request.args.get("identifier")
    usage = request.args.get("usage")
    return render_template("meter_upload_successfully.html")


# quit the whole system (not finished yet)
@app.route("/company/quit")
def quit_app():
    pass

@app.route('/stopServer', methods = ['GET'])
def stop_server():
    global acceptAPI
    acceptAPI = False
    batchJobs()
    acceptAPI = True
    return "Server Shutting Down"      


   
if __name__ == '__main__':
    # global df_ele
    load_data() # load admin and users profile before initiating the app
    try:
        app.run(debug=False) # using debug = True will result in anaconda bugs, how to fix it?
    except:
        print('something went wrong.')
