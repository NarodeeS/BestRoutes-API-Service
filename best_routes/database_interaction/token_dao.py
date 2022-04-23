import random
import string
from best_routes.database_interaction.models import Token
from .database import db_session


def add_token(user_id: int) -> Token:
    new_token_value = str(user_id) + ":" + ''.join(random.SystemRandom()
                                                   .choice(string.ascii_letters + string.digits)
                                                   for _ in range(25))
    new_token = Token(value=new_token_value, user_id=user_id)
    db_session.add(new_token)
    db_session.commit()
    return new_token


def delete_token(token: Token) -> None:
    db_session.delete(token)
    db_session.commit()


def get_tokens_by_user_id(user_id: int) -> list:
    tokens = db_session.query(Token).filter(Token.user_id == user_id)
    return tokens
