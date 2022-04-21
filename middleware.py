from flask import request, make_response, jsonify
from sqlalchemy.exc import PendingRollbackError
from best_routes.utils import check_login
from best_routes.exceptions import ServiceNotRespondException, \
    NoSuchAirportException, NoSuchRoutesException, UserAlreadyExistsException


def auth(processing_function):
    def wrapper(*args, **kwargs):
        user_token = request.headers.get("Token")
        if user_token is None:
            return make_response(jsonify(status="error", message="Token required"), 401)
        if check_login(user_token):
            return processing_function(*args, **kwargs)
        else:
            return make_response(jsonify(status="error", message="Incorrect token"), 403)
    wrapper.__name__ = processing_function.__name__
    return wrapper


def exception_handler(processing_function):
    def wrapper(*args, **kwargs):
        try:
            return processing_function(*args, **kwargs)
        except (ValueError, KeyError):
            message = jsonify(message="incorrect request format", status="error")
            return make_response(message, 400)
        except (ConnectionError, ServiceNotRespondException) as e:
            return make_response(jsonify(status="error", message=str(e)), 500)
        except PendingRollbackError as e:
            print(str(e))
            return make_response(jsonify(status="error",
                                         message=f"PendingRollbackError while working with database"))
        except (NoSuchRoutesException, NoSuchAirportException, UserAlreadyExistsException) as e:
            return make_response(jsonify(status="error", message=str(e)), 400)
    wrapper.__name__ = processing_function.__name__
    return wrapper
