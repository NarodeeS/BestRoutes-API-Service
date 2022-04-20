from flask import Flask, request, make_response, jsonify
from datetime import datetime, date
from best_routes.utils import create_token, create_user, \
    create_tracked_avia_direction, create_tracked_avia_trip, DirectionsManagerThread
from best_routes import session, User
from best_routes.transport_utils.avia_routes import get_avia_routes_from_service, get_avia_routes, \
    get_avia_trips_from_service, get_avia_trips, AviaService
from best_routes.transport_utils.railway_routes import get_routes_from_rzd, get_routes_from_rzd_return
from werkzeug.security import generate_password_hash, check_password_hash
from middleware import auth, exception_handler
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
directions_manager = DirectionsManagerThread(float(os.getenv("CHECK_TIME")))
directions_manager.start()


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
    supposed_user = session.query(User).filter(User.email == email).first()
    if supposed_user is not None:
        if check_password_hash(supposed_user.password, password):
            if content.get("telegramId") is not None:
                supposed_user.telegram_id = content["telegramId"]
                session.commit()
                session.rollback()
            user_token = create_token(supposed_user.id)
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
    new_user = create_user(email, hashed_password, telegram_id)
    new_user_token = create_token(new_user.id)
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
            session.delete(token)
            session.commit()
            session.rollback()
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
    if departure_date > date.today():
        raise ValueError()
    service_class = content["serviceClass"]
    adult = content["adult"]
    child = content["child"]
    infant = content["infant"]
    min_cost = content["baseMinCost"]
    create_tracked_avia_direction(user_id, departure_code,
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
    create_tracked_avia_trip(user_id, departure_code, arrival_code, departure_date1,
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


def __get_current_user() -> User:
    user_token = request.headers.get("Token")
    user_id = int(user_token.split(":")[0])
    user = session.query(User).filter(User.id == user_id).first()
    return user


def __process_item(collection: list, item_id: int):
    for item in collection:
        if item.id == item_id:
            if request.method == "GET":
                return make_response(jsonify(status="OK", result=item.to_json()), 200)
            elif request.method == "DELETE":
                session.delete(item)
                session.commit()
                session.rollback()
                return make_response(jsonify(status="OK", message="Deleted successfully"), 200)
    return make_response(jsonify(status="error", message="No such item"), 404)


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))

