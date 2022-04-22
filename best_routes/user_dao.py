from best_routes.models import User
from best_routes.exceptions import UserAlreadyExistsException
from best_routes import db


def get_user_by_id(user_id: int) -> User:
    user = User.query.filter_by(id=user_id).first()
    return user


def get_user_by_email(user_email: int) -> User:
    user = User.query.filter_by(email=user_email).first()
    return user


def update_user_telegram_id(user_id: int, telegram_id: str) -> None:
    user = User.query.filter_by(id=user_id).first()
    user.telegram_id = telegram_id
    db.session.commit()


def add_user(email: str, hashed_password: str, telegram_id: str, is_developer: bool) -> User:
    user = User.query.filter_by(email=email).first()
    if user is not None:
        raise UserAlreadyExistsException(email)
    new_user = User(email=email, password=hashed_password,
                    telegram_id=telegram_id, is_developer=is_developer)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_all_users() -> list:
    users = User.query.all()
    return users
