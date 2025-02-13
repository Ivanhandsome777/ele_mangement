# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 21:56:20 2025

@author: 30048
"""

# Source: Geeksforgeeks
import csv
import os 
from flask import Flask, request, redirect, url_for

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
@app.route("/", methods=["GET", "POST"])
def mainsite():



@app.route("/User",methods=["GET","POST"])
def user_query():
    pass

    return 


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
    load_data() # load admin and users profile before initiating the app
    try:
        app.run(debug=False) # using debug = True will result in anaconda bugs, how to fix it?
    finally:
        save_data() # save changes on the users profile