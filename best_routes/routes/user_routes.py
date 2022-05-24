import os
from datetime import date
from flask import Blueprint, request, jsonify, make_response
from best_routes.middleware import exception_handler, auth
from werkzeug.security import generate_password_hash, check_password_hash
from best_routes.database_interaction import add_user, add_token, get_user_by_email, \
    delete_token, get_current_user, add_avia_direction, process_item, add_avia_trip

user_blueprint = Blueprint("user_blueprint", __name__)


@user_blueprint.route("/user/register", methods=["POST"])
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


@user_blueprint.route("/user/login", methods=["POST"])
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


@user_blueprint.route("/user/quit", methods=["POST"])
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


@user_blueprint.route("/user/track/avia", methods=["POST"])
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


@user_blueprint.route("/user/track/avia", methods=["GET"])
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


@user_blueprint.route("/user/track/avia/<int:direction_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia(direction_id: int):
    user = get_current_user()
    return process_item(user.tracked_avia_directions, direction_id)


@user_blueprint.route("/user/track/avia/trip", methods=["POST"])
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


@user_blueprint.route("/user/track/avia/trip", methods=["GET"])
@exception_handler
@auth
def user_track_avia_trip_get_all():
    user = get_current_user()
    return make_response(jsonify(status="OK",
                                 result=[trip.to_json() for trip in user.tracked_avia_trips]))


@user_blueprint.route("/user/track/avia/trip/<int:trip_id>", methods=["GET", "DELETE"])
@exception_handler
@auth
def user_track_avia_trip(trip_id: int):
    user = get_current_user()
    return process_item(user.tracked_avia_trips, trip_id)
