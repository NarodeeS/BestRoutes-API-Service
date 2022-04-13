from flask import request, make_response, jsonify
from best_routes import check_login
from best_routes.exceptions import ServiceNotRespondException, \
    NoSuchAirportException, NoSuchRoutesException


def auth(processing_function):
    def wrapper():
        user_token = request.headers.get("Token")
        if user_token is None:
            return {"status": "error", "message": "token required"}
        if check_login(user_token):
            return processing_function()
        else:
            return {"status": "error", "message": "incorrect token"}
    wrapper.__name__ = processing_function.__name__
    return wrapper


def exception_handler(processing_function):
    def wrapper():
        try:
            return processing_function()
        except (ValueError, KeyError):
            message = jsonify(message="incorrect request format", status="error")
            return make_response(message, 400)
        except (ServiceNotRespondException, NoSuchRoutesException, NoSuchAirportException) as e:
            return {"status": "error", "message": str(e)}
    wrapper.__name__ = processing_function.__name__
    return wrapper
