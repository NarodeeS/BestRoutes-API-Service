import flask
from best_routes import app
from flask import request, make_response, jsonify, render_template, url_for, redirect, session
from datetime import datetime, date
from best_routes.delete_item import delete_item
from best_routes.user_dao import add_user, get_user_by_email, update_user_telegram_id, get_user_by_id
from best_routes.token_dao import add_token, delete_token
from best_routes.avia_direction_dao import add_avia_direction
from best_routes.avia_trip_dao import add_avia_trip
from best_routes.service_dao import activate_service, add_service, delete_service
from best_routes.transport_utils.avia_routes import get_avia_routes_from_service, get_avia_routes, \
    get_avia_trips_from_service, get_avia_trips, AviaService
from best_routes.transport_utils.railway_routes import get_routes_from_rzd, get_routes_from_rzd_return
from werkzeug.security import generate_password_hash, check_password_hash
from best_routes.middleware import auth, exception_handler
import os


@app.route("/routes/avia", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia():
    return make_response(jsonify(result=get_avia_routes(request.get_json()), status="OK"), 200)


@app.route("/routes/avia/trips", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_trip():
    return make_response(jsonify(result=get_avia_trips(request.get_json()), status="OK"), 200)


@app.route("/routes/avia/tutu", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_tutu():
    return make_response(jsonify(result=get_avia_routes_from_service(AviaService.TUTU, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/trips/tutu", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_tutu_trip():
    return make_response(jsonify(result=get_avia_trips_from_service(AviaService.TUTU, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/kupibilet", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_kupibilet():
    return make_response(jsonify(result=get_avia_routes_from_service(AviaService.KUPIBILET, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/trips/kupibilet", methods=["GET", "POST"])
@exception_handler
@auth
def routes_avia_kupibilet_trip():
    return make_response(jsonify(result=get_avia_trips_from_service(AviaService.KUPIBILET, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/railway/rzd", methods=["GET", "POST"])
@exception_handler
@auth
def routes_railway_rzd():
    content = request.get_json()
    from_station_code = content["fromStationCode"]  # Express 3 format
    from_station_node_id = content["fromStationNodeId"]  # from RZD suggests API
    to_station_code = content["toStationCode"]
    to_station_node_id = content["toStationNodeId"]
    departure_datetime = datetime.fromisoformat(content["departureDatetime"])
    count = content["count"]
    result = get_routes_from_rzd(from_station_code, from_station_node_id,
                                 to_station_code, to_station_node_id,
                                 departure_datetime, count)
    return make_response(jsonify(result=result, status="OK"), 200)


@app.route("/routes/railway/trips/rzd", methods=["GET", "POST"])
@exception_handler
@auth
def routes_railway_rzd_trip():
    content = request.get_json()
    from_station_code = content["fromStationCode"]
    from_station_node_id = content["fromStationNodeId"]
    to_station_code = content["toStationCode"]
    to_station_node_id = content["toStationNodeId"]
    departure_datetime1 = datetime.fromisoformat(content["departureDatetime1"])
    departure_datetime2 = datetime.fromisoformat(content["departureDatetime2"])
    count = content["count"]
    result = get_routes_from_rzd_return(from_station_code, from_station_node_id, to_station_code,
                                        to_station_node_id, departure_datetime1, departure_datetime2, count)
    return make_response(jsonify(result=result, status="OK"), 200)


@app.route("/user/login", methods=["POST"])
@exception_handler
def user_login():
    content = request.get_json()
    email = content["email"]
    password = content["password"]
    if email is None or password is None:
        raise ValueError
    supposed_user = get_user_by_email(email)
    if supposed_user is not None:
        if check_password_hash(supposed_user.password, password):
            if content.get("telegramId") is not None:
                update_user_telegram_id(supposed_user.id, content.get("telegramId"))
            user_token = add_token(supposed_user.id)
            response = make_response(jsonify(status="OK"), 200)
            response.headers.add("Token", user_token.value)
            return response
        return make_response(jsonify(status="error", message="Wrong credentials"), 403)
    else:
        return make_response(jsonify(status="error", message="No such user"), 401)


@app.route("/user/register", methods=["POST"])
@exception_handler
def user_register():
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
    telegram_id = None
    if content.get("telegramId") is not None:
        telegram_id = content["telegramId"]
    new_user = add_user(email, hashed_password, telegram_id, False)
    new_user_token = add_token(new_user.id)
    response = make_response(jsonify(status="OK"), 200)
    response.headers.add("Token", new_user_token.value)
    return response


@app.route("/user/quit", methods=["POST"])
@exception_handler
@auth
def user_quit():
    user_token = request.headers.get("Token")
    user_tokens = __get_current_user().tokens
    for token in user_tokens:
        if token.value == user_token:
            delete_token(token)
            return make_response(jsonify(status="OK"), 200)
    return make_response(jsonify(status="error", message="No user with such token"))


@app.route("/user/track/avia", methods=["POST"])
@exception_handler
@auth
def user_track_avia_add():
    user_id = __get_current_user().id
    content = request.get_json()
    departure_code = content["departureCode"]
    arrival_code = content["arrivalCode"]
    departure_date = date.fromisoformat(content["departureDate"])
    if departure_date < date.today():
        raise ValueError()
    service_class = content["serviceClass"]
    adult = content["adult"]
    child = content["child"]
    infant = content["infant"]
    min_cost = content["baseMinCost"]
    add_avia_direction(user_id, departure_code,
                       arrival_code, departure_date, service_class,
                       adult, child, infant, min_cost, False)
    return make_response(jsonify(status="OK"), 200)


@app.route("/user/track/avia", methods=["GET"])
@exception_handler
@auth
def user_track_avia_get_all():
    user = __get_current_user()
    return make_response(jsonify(status="OK",
                                 result=[direction.to_json() for direction in user.tracked_avia_directions]))


@app.route("/user/track/avia/<int:direction_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia(direction_id: int):
    user = __get_current_user()
    return __process_item(user.tracked_avia_directions, direction_id)


@app.route("/user/track/avia/trip", methods=["POST"])
@exception_handler
@auth
def user_track_avia_trip_add():
    user_token = request.headers.get("Token")
    user_id = int(user_token.split(":")[0])
    content = request.get_json()
    departure_code = content["departureCode"]
    arrival_code = content["arrivalCode"]
    departure_date1 = date.fromisoformat(content["departureDate1"])
    departure_date2 = date.fromisoformat(content["departureDate2"])
    service_class = content["serviceClass"]
    adult = content["adult"]
    child = content["child"]
    infant = content["infant"]
    min_cost1 = content["baseMinCost1"]
    min_cost2 = content["baseMinCost2"]
    add_avia_trip(user_id, departure_code, arrival_code, departure_date1,
                  departure_date2, service_class, adult, child,
                  infant, min_cost1, min_cost2)
    return make_response(jsonify(status="OK"), 200)


@app.route("/user/track/avia/trip", methods=["GET"])
@exception_handler
@auth
def user_track_avia_trip_get_all():
    user = __get_current_user()
    return make_response(jsonify(status="OK",
                                 result=[trip.to_json() for trip in user.tracked_avia_trips]))


@app.route("/user/track/avia/trip/<int:trip_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia_trip(trip_id: int):
    user = __get_current_user()
    return __process_item(user.tracked_avia_trips, trip_id)


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
                        return make_response(jsonify(status="error", message="User is not a developer"), 401)
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
            user = add_user(email, hashed_password, None, True)

        session["user_id"] = user.id
        return redirect(url_for("developer_home"))

    else:
        return render_template("developer_login.html")


@app.route("/developer/home", methods=["GET"])
@exception_handler
def developer_home():
    if flask.session.get("user_id") is not None:
        user_id = session.get("user_id")
        user_services = __get_current_user(user_id).services
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


@app.route("/developer/service/delete/<int:service_id>", methods=["POST"])
@exception_handler
def developer_service_delete(service_id: int):
    delete_service(service_id)
    return redirect(url_for("developer_home"))


@app.route("/developer/service/activate/<int:service_id>", methods=["POST"])
@exception_handler
def developer_service_activate(service_id: int):
    activate_service(service_id)
    return redirect(url_for("developer_home"))


def __get_current_user(passed_user_id: int = None):
    user = None
    if passed_user_id is not None:
        user = get_user_by_id(passed_user_id)
    else:
        user_token = request.headers.get("Token")
        user_id = int(user_token.split(":")[0])
        user = get_user_by_id(user_id)
    return user


def __process_item(collection: list, item_id: int):
    for item in collection:
        if item.id == item_id:
            if request.method == "GET":
                return make_response(jsonify(status="OK", result=item.to_json()), 200)
            elif request.method == "DELETE":
                delete_item(item)
                return make_response(jsonify(status="OK", message="Deleted successfully"), 200)
    return make_response(jsonify(status="error", message="No such item"), 404)
