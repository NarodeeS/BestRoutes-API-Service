from .database import session
from .models import User


def create_user(email: str, hashed_password: str, telegram_id: str):
    new_user = User(email=email, password=hashed_password, telegram_id=telegram_id)
    session.add(new_user)
    session.commit()
    session.rollback()
    return new_user
