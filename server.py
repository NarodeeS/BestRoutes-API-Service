from flask import Flask, request, make_response, jsonify
from best_routes import session, create_token, create_user, User, Token
from best_routes.transport_utils.avia_routes import get_avia_routes_from_service, get_avia_routes, \
    get_avia_trips_from_service, get_avia_trips, AviaService
from best_routes.transport_utils.railway_routes import get_routes_from_rzd, get_routes_from_rzd_return
from werkzeug.security import generate_password_hash, check_password_hash
from middleware import auth, exception_handler
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)


@app.route("/routes/avia", methods=["GET", "POST"])
@auth
@exception_handler
def routes_avia():
    return make_response(jsonify(result=get_avia_routes(request.get_json()), status="OK"), 200)


@app.route("/routes/avia/trips", methods=["GET", "POST"])
@auth
@exception_handler
def routes_avia_trip():
    return make_response(jsonify(result=get_avia_trips(request.get_json()), status="OK"), 200)


@app.route("/routes/avia/tutu", methods=["GET", "POST"])
@auth
@exception_handler
def routes_avia_tutu():
    return make_response(jsonify(result=get_avia_routes_from_service(AviaService.TUTU, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/tutu/trips", methods=["GET", "POST"])
@auth
@exception_handler
def routes_avia_tutu_trip():
    return make_response(jsonify(result=get_avia_trips_from_service(AviaService.TUTU, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/kupibilet", methods=["GET", "POST"])
@auth
@exception_handler
def routes_avia_kupibilet():
    return make_response(jsonify(result=get_avia_routes_from_service(AviaService.KUPIBILET, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/kupibilet/trips", methods=["GET", "POST"])
@auth
def routes_avia_kupibilet_trip():
    return make_response(jsonify(result=get_avia_trips_from_service(AviaService.KUPIBILET, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/railway/rzd", methods=["GET", "POST"])
@auth
@exception_handler
def routes_railway_rzd():
    content = request.get_json()
    from_station_code = content["fromStationCode"]  # Express 3 format
    from_station_node_id = content["fromStationNodeId"]  # from RZD suggests API
    to_station_code = content["toStationCode"]
    to_station_node_id = content["toStationNodeId"]
    departure_datetime = content["departureDatetime"]
    result = get_routes_from_rzd(from_station_code, from_station_node_id,
                                 to_station_code, to_station_node_id, departure_datetime)
    return make_response(jsonify(result=result, status="OK"), 200)


@app.route("/routes/railway/rzd/trips", methods=["GET", "POST"])
@auth
@exception_handler
def routes_railway_rzd_trip():
    content = request.get_json()
    from_station_code = content["fromStationCode"]
    from_station_node_id = content["fromStationNodeId"]
    to_station_code = content["toStationCode"]
    to_station_node_id = content["toStationNodeId"]
    departure_datetime1 = content["departureDatetime1"]
    departure_datetime2 = content["departureDateTime2"]
    result = get_routes_from_rzd_return(from_station_code, from_station_node_id, to_station_code,
                                        to_station_node_id, departure_datetime1, departure_datetime2)
    return make_response(jsonify(result=result, status="OK"), 200)


@app.route("/users/login", methods=["POST"])
@exception_handler
def user_login():
    content = request.get_json()
    email = content["email"]
    password = content["password"]
    if email is None or password is None:
        raise ValueError
    supposed_user = session.query(User).filter(User.email == email).first()
    print(supposed_user.email)
    if check_password_hash(supposed_user.password, password):
        user_token = create_token(supposed_user.id)
        response = make_response(jsonify(status="OK"), 200)
        response.headers.add("Token", user_token.value)
        return response
    return {"Status": "error", "message": "wrong credentials"}


@app.route("/users/register", methods=["POST"])
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
    telegram_id = request.headers.get("telegramId")
    new_user = create_user(email, hashed_password, telegram_id)
    new_user_token = create_token(new_user.id)
    response = make_response(jsonify(status="OK"), 200)
    response.headers.add("Token", new_user_token)
    return response


@app.route("/users/quit", methods=["POST"])
@exception_handler
def user_quit():
    user_token = request.headers.get("Token")
    user_id = user_token.split(":")[0]
    user_tokens = session.query(Token).filter(Token.user_id == user_id)
    for token in user_tokens:
        if token.value == user_token:
            session.delete(token)
            session.commit()
            session.rollback()
            return {"status": "OK"}
    return {"status": "error", "message": "no user with such token"}


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))
