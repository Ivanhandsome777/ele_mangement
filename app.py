# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 21:56:20 2025

@author: 30048
"""

# Source: Geeksforgeeks
from flask import Flask, request, redirect, url_for,render_template
import os
import csv

app = Flask(__name__)
# read user table and active machine list CSV everytime when initiate the process
# create empty user dictionary for user register, modity, and deactivate
admins = {} # {email address, password}
users = {} # { identifier: {address, region, sub_region, postcode, apartment_type} }

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
@app.route("/", methods=["GET","POST"])
def mainsite():
    return(render_template('home.html'))


@app.route("/user",methods=["GET","POST"])
def user_query():

    return(render_template('user_login.html'))

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