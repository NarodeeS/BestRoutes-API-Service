from flask import request, make_response, jsonify
from sqlalchemy.exc import PendingRollbackError, SQLAlchemyError
from best_routes.utils import logger
from best_routes.utils import Log
from best_routes.database_interaction import check_login
from best_routes.exceptions import ServiceNotRespondException, \
    NoSuchCityException, NoSuchRoutesException, UserAlreadyExistsException


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
        except KeyError:
            return make_response(jsonify(message="incorrect request parameters", status="error"), 400)
        except ValueError:
            return make_response(jsonify(message="incorrect request values", status="error"), 400)
        except ConnectionError:
            return make_response(jsonify(status="error", message="problems with connection"), 500)
        except ServiceNotRespondException:
            return make_response(jsonify(status="error", message="service not respond"), 500)
        except PendingRollbackError:
            return make_response(jsonify(status="error",
                                         message=f"Something went wrong. Try again"))
        except SQLAlchemyError as e:
            logger.add_log(Log("SQLAlchemyError", e.__cause__, "middleware.py", processing_function.__name__))
        except (NoSuchRoutesException, NoSuchCityException, UserAlreadyExistsException) as e:
            return make_response(jsonify(status="error", message=str(e)), 400)
    wrapper.__name__ = processing_function.__name__
    return wrapper
