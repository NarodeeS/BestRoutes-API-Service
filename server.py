from flask import Flask, request, make_response, jsonify
from best_routes import session, generate_token, User, Token
from best_routes.transport_utils.avia_routes import get_routes_from, AviaService
from werkzeug.security import generate_password_hash, check_password_hash
from middleware import auth, exception_handler
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)


@app.route("/routes/avia", methods=["GET"])
@auth
def routes_avia():
    pass


@app.route("/routes/avia/tutu", methods=["GET"])
@auth
@exception_handler
def routes_tutu():
    return make_response(jsonify(result=get_routes_from(AviaService.TUTU, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/avia/kupibilet", methods=["GET"])
@auth
@exception_handler
def routes_kupibilet():
    return make_response(jsonify(result=get_routes_from(AviaService.KUPIBILET, request.get_json()),
                                 status="OK"), 200)


@app.route("/routes/railway/route", methods=["GET"])
@auth
def railway_routes():
    pass


@app.route("/routes/railway/trip", methods=["GET"])
@auth
def railway_trips():
    pass


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
        user_token = Token(value=generate_token(email[0: email.index("@")]),
                           user_id=supposed_user.id)
        session.add(user_token)
        session.commit()
        session.rollback()
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


@app.route("/users/quit", methods=["POST"])
def user_quit():
    pass


@app.route("/users/routes/avia-routes", methods=["GET", "POST"])
@auth
def user_tracked_avia_routes():
    pass


if __name__ == "__main__":
    app.run(debug=True, host=os.environ.get("HOST"), port=os.environ.get("PORT"))
