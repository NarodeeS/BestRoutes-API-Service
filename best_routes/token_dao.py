import random
import string
from best_routes.models import Token
from best_routes import db


def add_token(user_id: int) -> Token:
    new_token_value = str(user_id) + ":" + ''.join(random.SystemRandom()
                                                   .choice(string.ascii_letters + string.digits)
                                                   for _ in range(25))
    new_token = Token(value=new_token_value, user_id=user_id)
    db.session.add(new_token)
    db.session.commit()
    return new_token


def delete_token(token: Token) -> None:
    db.session.delete(token)
    db.session.commit()


def get_tokens_by_user_id(user_id: int) -> list:
    tokens = Token.query.filter_by(user_id=user_id).all()
    return tokens
