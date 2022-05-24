import os
from flask import Blueprint, session, redirect, url_for, request, make_response, jsonify, render_template
from best_routes.middleware import exception_handler
from best_routes.database_interaction import get_user_by_email, make_user_developer, add_user, \
    get_user_by_id, add_service, check_service_belonging, activate_service, delete_service
from werkzeug.security import generate_password_hash, check_password_hash


developer_blueprint = Blueprint("developer_blueprint", __name__)


@developer_blueprint.route("/developer/auth", methods=["GET", "POST"])
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


@developer_blueprint.route("/developer/quit", methods=["POST", "GET"])
@exception_handler
def developer_quit():
    session.pop("user_id")
    return redirect(url_for("developer_auth"))


@developer_blueprint.route("/developer/home", methods=["GET"])
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


@developer_blueprint.route("/developer/service", methods=["POST"])
@exception_handler
def developer_service_add():
    service_name = request.form.get("service_name")
    service_url = request.form.get("service_url")
    developer_id = session.get("user_id")
    add_service(service_name, service_url, developer_id)
    return redirect(url_for("developer_home"))


@developer_blueprint.route("/developer/service/delete/<int:service_id>", methods=["POST", "GET"])
@exception_handler
def developer_service_delete(service_id: int):
    if check_service_belonging(session.get("user_id"), service_id):
        delete_service(service_id)
        return redirect(url_for("developer_home"))
    else:
        return make_response(jsonify(status="error", message="This user does not have such service"))


@developer_blueprint.route("/developer/service/activate/<int:service_id>", methods=["POST", "GET"])
@exception_handler
def developer_service_activate(service_id: int):
    if check_service_belonging(session.get("user_id"), service_id):
        activate_service(service_id)
        return redirect(url_for("developer_home"))
    else:
        return make_response(jsonify(status="error", message="This user does not have such service"))
