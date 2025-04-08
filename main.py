import user_management1 as dbHandler
import bcrypt
from flask import Flask
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask import render_template
from flask import request
from flask import redirect
import logging
import re

def sanitize_input(inputSan):
    return re.sub(r'[<>"\']', '', str(inputSan)) if inputSan else ""

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        feedback = sanitize_input(request.form.get("feedback"))
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        dbHandler.insertUser(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        username = request.form.get('username')
        session["name"] = username  # Store in session
        return redirect("/")
    #return render_template("/index.html")

    if not session.get("name"): # First check if user is logged in
        return redirect("/login")
    #return render_template("index.html") #keep an eye on this line
        
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            session["name"] = username  # Store in session
            dbHandler.listFeedback()
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Record the user name in session
        session["name"] = request.form.get("name")
        return redirect("/")
    return render_template("login.html")
#@app.route("/login", methods=["GET", "POST"])
#def login():
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            session["name"] = username
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="127.0.0.1", port=5000)
