from . import app
from check_login import check_login
from flask import request


# check_login
@app.route("/routes/avia", methods=["GET"])
def get_routes():
    pass


# check_login
@app.route("/routes/avia/tutu", methods=["GET"])
def get_routes_from_tutu():
    pass


# check_login
@app.route("/routes/avia/kupibilet", methods=["GET"])
def get_routes_from_kupibilet():
    pass


# check_login
@app.route("/routes/railway", methods=["GET"])
def get_railway_routes():
    pass


@app.route("/users/login", methods=["POST"])
def user_login():
    pass


@app.route("/users/register", methods=["POST"])
def user_register():
    pass


@app.route("/users/quit", methods=["POST"])
def user_quit():
    pass


# check_login
@app.route("/users/routes/avia-routes", methods=["GET", "POST"])
def user_get_tracked_avia_routes():
    pass


