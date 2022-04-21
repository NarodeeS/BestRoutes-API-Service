from .database import Session
from best_routes import database
from sqlalchemy.exc import SQLAlchemyError, DatabaseError


def database_operation_wrapper(database_function):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = database_function(*args, **kwargs)
            database.session.commit()
        except SQLAlchemyError as e:
            print(str(e))
        finally:
            database.session.rollback()
            return result
    return wrapper
