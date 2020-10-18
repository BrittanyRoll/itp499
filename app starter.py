from flask import Flask, redirect, render_template, request, session, url_for
import os
import sqlite3 as sl

app = Flask(__name__)
db = "favouriteFoods.db"
conn = sl.connect(db, check_same_thread=False)  # connect to database
curs = conn.cursor()

@app.route("/")
def home():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        if session["username"] == "admin":
            return render_template("admin.html", username=session["username"], result=db_get_user_list())
        else:
            return render_template("user.html", username=session["username"], fav_food=db_get_food(session["username"]))
    pass


@app.route("/client")
def client():
    pass


@app.route("/action/createuser", methods=["POST", "GET"])
def create_user():
    if request.method == "POST":
        db_create_user(request.form["username"], request.form["password"])
        res = db_get_user_list()
        return render_template("admin.html", username=request.form["username"], result=res)
    pass


@app.route("/action/removeuser", methods=["POST", "GET"])
def remove_user():
    if request.method == "POST":
        db_remove_user(request.form["username"])
        res = db_get_user_list()
        return render_template("admin.html", username=request.form["username"], result=res)
    pass


@app.route("/action/setfood", methods=["POST", "GET"])
def set_food():
    if request.method == "POST":
        db_set_food(session["username"], request.form["set_fav_food"])
        session["fav_food"] = db_get_food(session["username"])
        return render_template("user.html", username=session["username"], fav_food=db_get_food(session["username"]))
    pass


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "password":
            session["username"] = request.form["username"]
            session["logged_in"] = True
            res = db_get_user_list()
            return render_template("admin.html", username=request.form["username"], result=res)
        else:
            exists = db_check_creds(request.form["username"], request.form["password"])
            if exists:
                session["username"] = request.form["username"]
                session["logged_in"] = True
                fav = db_get_food(session["username"])
                return render_template("user.html", username=request.form["username"], fav_food=fav)
        return render_template("login.html")
    pass


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if request.method == "POST":
        session["logged_in"] = False
        return render_template("login.html")
    pass



def db_get_user_list():
    get_user_list = "SELECT * from userfoods"
    curs.execute(get_user_list)
    rows = curs.fetchall()
    dict1 = {}
    for i in rows:
        name = i[0]
        food = i[1]
        dict1[name] = food
    return dict1


def db_create_user(un, pw):
    creat_user = "INSERT INTO credentials (username, password) VALUES (?, ?)"
    create_user2 = "INSERT INTO userfoods (username, food) VALUES (?, ?)"  # not sure
    curs.execute(creat_user, (un, pw))
    curs.execute(create_user2, (un, None))


def db_remove_user(un):
    remov_user = "DELETE FROM credentials WHERE username=?"
    remove_user2 = "DELETE FROM userfoods WHERE username=?"
    curs.execute(remov_user, (un,))
    curs.execute(remove_user2, (un,))


def db_get_food(un):
    get_food_stmt = "SELECT food FROM userfoods WHERE username=?"
    curs.execute(get_food_stmt, (un,))
    food = curs.fetchall()
    return food[0][0]


def db_set_food(un, ff):
    enter_food = "UPDATE userfoods SET food=? WHERE username=?"
    curs.execute(enter_food, (ff, un))


def db_check_creds(un, pw):
    login_user = "SELECT EXISTS(SELECT 1 FROM credentials WHERE username=? AND password=?)"  # not sure if this will work
    real_user = curs.execute(login_user, (un, pw))
    return real_user


# -----------------------------------------
# # admin
# get_user_list = "SELECT * from userfoods"
# data = curs.execute(get_user_list)
#
#
# # login and create, need to check if already exists?
# create_user = "INSERT INTO credentials (username, password) VALUES (?, ?)"
# # or?
# create_user = "INSERT INTO credentials VALUES (?, ?)"
# # and
# create_user2 = "INSERT INTO userfoods VALUE ?"  # not sure
# curs.execute(create_user, (un, pw))
# curs.execute(create_user2, un)
#
# login_user = "SELECT EXISTS(SELECT 1 FROM credentials WHERE username=? AND password=?"  # not sure if this will work
# real_user = curs.execute(login_user, (un, pw))
#
#
# # remove user
# remove_user = "DELETE FROM credentials WHERE username=?"
# remove_user2 = "DELETE FROM userfoods WHERE username=?"
# curs.execute(remove_user, un)
# curs.execute(remove_user2, un)
#
#
# # food
# get_food_stmt = "SELECT * from userfoods WHERE username=?"
# # or
# get_food_stmt = "SELECT food from userfoods WHERE username=?"
# data = curs.execute(get_food_stmt, un)
#
# enter_food = "UPDATE userfoods SET food=? WHERE username=?"
# curs.execute(enter_food, (ff, un))
# -----------------------------------------


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)