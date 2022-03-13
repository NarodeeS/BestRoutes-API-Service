from flask import Flask, request, make_response, jsonify
from best_routes import session, generate_token, User, Token, check_login
from best_routes.transport_utils.avia_routes import get_routes_from_kupibilet
from best_routes.transport_utils.exceptions import ServiceNotRespondException
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import date
import os


load_dotenv()
app = Flask(__name__)


# check_login
@app.route("/routes/avia", methods=["GET"])
def routes():
    pass


# check_login
@app.route("/routes/avia/tutu", methods=["GET"])
def utes_tutu():
    pass


# check_login
@app.route("/routes/avia/kupibilet", methods=["GET"])
def routes_kupibilet():
    user_token = request.headers.get("Token")
    if user_token is None:
        return {"status": "error", "message": "token required"}
    if check_login(user_token):
        content = request.get_json()
        departure_code = content["departureCode"]
        arrival_code = content["arrivalCode"]
        departure_date = date.fromisoformat(content["departureDate"])
        service_class = content["serviceClass"]
        adult = content["adult"]
        child = content["child"]
        infant = content["infant"]
        try:
            kupibilet_routes = get_routes_from_kupibilet(departure_code, arrival_code,
                                                         departure_date, adult, child, infant, service_class)
            return make_response(jsonify(result=list([route.to_json() for route in kupibilet_routes]),
                                         status="OK"), 200)
        except ServiceNotRespondException:
            return {"status": "error", "message": "service not respond. Maybe wrong route params?"}
    else:
        return {"status": "error", "message": "incorrect token"}


# check_login
@app.route("/routes/railway/route", methods=["GET"])
def railway_routes():
    pass


# check_login
@app.route("/routes/railway/trip", methods=["GET"])
def railway_trips():
    pass


@app.route("/users/login", methods=["POST"])
def user_login():
    try:
        content = request.get_json()
        email = content["email"]
        password = content["password"]
        if email is None or password is None:
            raise ValueError
        supposed_user = session.query(User).filter(User.email == email).first()
        print(supposed_user.email)
        if check_password_hash(supposed_user.password, password):
            user_token = Token(value=generate_token(email[0: email.index("@")]),
                               user_id=supposed_user.id)
            session.add(user_token)
            session.commit()
            session.rollback()
            response = make_response(jsonify(status="OK"), 200)
            response.headers.add("Token", user_token.value)
            return response
        return {"Status": "error", "message": "wrong credentials"}

    except ValueError:
        message = jsonify(message="incorrect request format", status="error")
        return make_response(message, 400)


@app.route("/users/register", methods=["POST"])
def user_register():
    try:
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
        new_user = User(email=email, password=hashed_password, telegram_id=telegram_id)
        session.add(new_user)
        session.commit()
        session.rollback()
        new_user_token = Token(value=generate_token(new_user.id),
                               user_id=new_user.id)
        session.add(new_user_token)
        session.commit()
        session.rollback()
        response = make_response(jsonify(status="OK"), 200)
        response.headers.add("Token", new_user_token.value)
        return response

    except ValueError:
        message = jsonify(message="incorrect request format", status="error")
        return make_response(message, 400)


@app.route("/users/quit", methods=["POST"])
def user_quit():
    pass


# check_login
@app.route("/users/routes/avia-routes", methods=["GET", "POST"])
def user_tracked_avia_routes():
    pass


if __name__ == "__main__":
    app.run(debug=True)
