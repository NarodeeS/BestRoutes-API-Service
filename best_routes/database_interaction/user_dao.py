from best_routes.database_interaction.models import User
from best_routes.exceptions import UserAlreadyExistsException
from .database import db_session


def get_user_by_id(user_id: int) -> User:
    user = db_session.query(User).filter(User.id == user_id).first()
    return user


def get_user_by_email(user_email: int) -> User:
    user = db_session.query(User).filter(User.email == user_email).first()
    return user


def update_user_telegram_id(user_id: int, telegram_id: str) -> None:
    user = db_session.query(User).filter(User.id == user_id).first()
    user.telegram_id = telegram_id
    db_session.commit()


def make_user_developer(user_id: int) -> None:
    user = db_session.query(User).filter(User.id == user_id).first()
    user.is_developer = True
    db_session.commit()


def add_user(email: str, hashed_password: str, telegram_id: str, is_developer: bool) -> User:
    user = db_session.query(User).filter(User.email == email).first()
    if user is not None:
        raise UserAlreadyExistsException(email)
    new_user = User(email=email, password=hashed_password,
                    telegram_id=telegram_id, is_developer=is_developer)
    db_session.add(new_user)
    db_session.commit()
    return new_user


def get_all_users() -> list:
    users = db_session.query(User)
    return users
