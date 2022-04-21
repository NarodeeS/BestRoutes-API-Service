from .database_operation_wrapper import database_operation_wrapper
from .database import session
from .models import User
from best_routes.exceptions import UserAlreadyExistsException


@database_operation_wrapper
def get_user_by_id(user_id: int) -> User:
    user = session.query(User).filter(User.id == user_id).first()
    return user


@database_operation_wrapper
def get_user_by_email(user_email: int) -> User:
    user = session.query(User).filter(User.email == user_email).first()
    return user


@database_operation_wrapper
def update_user_telegram_id(user: User, telegram_id: str) -> None:
    user.telegram_id = telegram_id


@database_operation_wrapper
def add_user(email: str, hashed_password: str, telegram_id: str, is_developer: bool) -> User:
    user = session.query(User).filter(User.email == email).first()
    if user is not None:
        raise UserAlreadyExistsException(email)
    new_user = User(email=email, password=hashed_password, telegram_id=telegram_id, is_developer=is_developer)
    session.add(new_user)
    return new_user


