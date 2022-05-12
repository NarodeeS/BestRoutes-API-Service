import os
from flask import redirect, session, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from best_routes.middleware import auth, exception_handler
from best_routes.database_interaction import *
from best_routes.transport_utils.avia_routes import get_avia_routes, get_avia_trips
from best_routes import app


@app.route("/routes/avia", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia():
    return make_response(jsonify(result=get_avia_routes(request.args), status="OK"), 200)


@app.route("/routes/avia/trips", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_trip():
    return make_response(jsonify(result=get_avia_trips(request.args), status="OK"), 200)


@app.route("/user/register", methods=["POST"])
@exception_handler
def user_register():
    if request.headers["Content-Type"] != "application/json":
        raise ValueError()
    content = request.get_json()
    email = content["email"]
    password = content["password"]
    if email is None or password is None:
        raise ValueError()
    hashed_password = generate_password_hash(
        password,
        os.environ.get("HASH_METHOD"),
        int(os.environ.get("SALT_ROUNDS"))
    )
    new_user = add_user(email, hashed_password, False)
    new_user_token = add_token(new_user.id)
    response = make_response(jsonify(status="OK", token=new_user_token.value), 200)
    return response


@app.route("/user/login", methods=["POST"])
@exception_handler
def user_login():
    if request.headers["Content-Type"] != "application/json":
        raise ValueError()
    content = request.get_json()
    email = content["email"]
    password = content["password"]
    if email is None or password is None:
        raise KeyError()
    supposed_user = get_user_by_email(email)
    if supposed_user is not None:
        if check_password_hash(supposed_user.password, password):
            user_token = add_token(supposed_user.id)
            response = make_response(jsonify(status="OK", token=user_token.value), 200)
            return response
        return make_response(jsonify(status="error", message="Wrong credentials"), 403)
    else:
        return make_response(jsonify(status="error", message="No such user"), 401)


@app.route("/user/quit", methods=["POST"])
@exception_handler
@auth
def user_quit():
    user_token = request.headers.get("Token")
    user_tokens = get_current_user().tokens
    for token in user_tokens:
        if token.value == user_token:
            delete_token(token)
            return make_response(jsonify(status="OK"), 200)
    return make_response(jsonify(status="error", message="No user with such token"))


@app.route("/user/track/avia", methods=["POST"])
@exception_handler
@auth
def user_track_avia_add():
    user_id = get_current_user().id
    args = request.args
    departure_code = args["departureCode"]
    arrival_code = args["arrivalCode"]
    departure_date = date.fromisoformat(request.args["departureDate"])
    service_class = args["serviceClass"]
    adult = args["adult"]
    child = args["child"]
    infant = args["infant"]
    min_cost = args["baseMinCost"]
    add_avia_direction(user_id, departure_code,
                       arrival_code, departure_date, service_class,
                       adult, child, infant, min_cost)
    return make_response(jsonify(status="OK"), 200)


@app.route("/user/track/avia", methods=["GET"])
@exception_handler
@auth
def user_track_avia_get_all():
    user = get_current_user()
    directions = []
    for direction in user.tracked_avia_directions:
        if not direction.in_trip:
            directions.append(direction)
    return make_response(jsonify(status="OK",
                                 result=[direction.to_json() for direction in directions]))


@app.route("/user/track/avia/<int:direction_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia(direction_id: int):
    user = get_current_user()
    return process_item(user.tracked_avia_directions, direction_id)


@app.route("/user/track/avia/trip", methods=["POST"])
@exception_handler
@auth
def user_track_avia_trip_add():
    user_token = request.headers.get("Token")
    user_id = int(user_token.split(":")[0])
    args = request.args
    departure_code = args["departureCode"]
    arrival_code = args["arrivalCode"]
    departure_date1 = date.fromisoformat(args["departureDate1"])
    departure_date2 = date.fromisoformat(args["departureDate2"])
    service_class = args["serviceClass"]
    adult = args["adult"]
    child = args["child"]
    infant = args["infant"]
    min_cost1 = args["baseMinCost1"]
    min_cost2 = args["baseMinCost2"]
    add_avia_trip(user_id, departure_code, arrival_code, departure_date1,
                  departure_date2, service_class, adult, child,
                  infant, min_cost1, min_cost2)
    return make_response(jsonify(status="OK"), 200)


@app.route("/user/track/avia/trip", methods=["GET"])
@exception_handler
@auth
def user_track_avia_trip_get_all():
    user = get_current_user()
    return make_response(jsonify(status="OK",
                                 result=[trip.to_json() for trip in user.tracked_avia_trips]))


@app.route("/user/track/avia/trip/<int:trip_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia_trip(trip_id: int):
    user = get_current_user()
    return process_item(user.tracked_avia_trips, trip_id)


@app.route("/developer/auth", methods=["GET", "POST"])
@exception_handler
def developer_auth():
    if session.get("user_id") is not None:
        return redirect(url_for("developer_home"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        action_type = request.form.get("action")
        user = None
        if action_type == "login":
            user = get_user_by_email(email)
            if user is not None:
                if check_password_hash(user.password, password):
                    if not user.is_developer:
                        make_user_developer(user.id)
                else:
                    return make_response(jsonify(status="error", message="Wrong credentials"), 403)
            else:
                return make_response(jsonify(status="error", message="No such user"), 401)
        elif action_type == "register":
            hashed_password = generate_password_hash(
                password,
                os.environ.get("HASH_METHOD"),
                int(os.environ.get("SALT_ROUNDS"))
            )
            user = add_user(email, hashed_password, True)

        session["user_id"] = user.id
        return redirect(url_for("developer_home"))
    else:
        return render_template("developer_login.html")


@app.route("/developer/quit", methods=["POST", "GET"])
@exception_handler
def developer_quit():
    session.pop("user_id")
    return redirect(url_for("developer_auth"))


@app.route("/developer/home", methods=["GET"])
@exception_handler
def developer_home():
    if session.get("user_id") is not None:
        user_id = session.get("user_id")
        user = get_user_by_id(user_id)
        if user is None:
            session.pop("user_id")
            return redirect(url_for("developer_auth"))
        user_services = get_user_by_id(user_id).services
        return render_template("developer_home.html", services=user_services)
    else:
        return redirect(url_for("developer_auth"))


@app.route("/developer/service", methods=["POST"])
@exception_handler
def developer_service_add():
    service_name = request.form.get("service_name")
    service_url = request.form.get("service_url")
    developer_id = session.get("user_id")
    add_service(service_name, service_url, developer_id)
    return redirect(url_for("developer_home"))


@app.route("/developer/service/delete/<int:service_id>", methods=["POST", "GET"])
@exception_handler
def developer_service_delete(service_id: int):
    if check_service_belonging(session.get("user_id"), service_id):
        delete_service(service_id)
        return redirect(url_for("developer_home"))
    else:
        return make_response(jsonify(status="error", message="This user does not have such service"))


@app.route("/developer/service/activate/<int:service_id>", methods=["POST", "GET"])
@exception_handler
def developer_service_activate(service_id: int):
    if check_service_belonging(session.get("user_id"), service_id):
        activate_service(service_id)
        return redirect(url_for("developer_home"))
    else:
        return make_response(jsonify(status="error", message="This user does not have such service"))
