from best_routes.database import session
from best_routes.models import User


def create_user(email: str, hashed_password: str, telegram_id: str) -> User:
    new_user = User(email=email, password=hashed_password, telegram_id=telegram_id)
    session.add(new_user)
    session.commit()
    session.rollback()
    return new_user
