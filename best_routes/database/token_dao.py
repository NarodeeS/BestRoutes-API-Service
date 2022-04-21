import random
import string
from .database_operation_wrapper import database_operation_wrapper
from .database import session
from .models import Token


@database_operation_wrapper
def add_token(user_id) -> Token:
    new_token_value = str(user_id) + ":" + ''.join(random.SystemRandom()
                                                   .choice(string.ascii_letters + string.digits)
                                                   for _ in range(25))
    new_token = Token(value=new_token_value, user_id=user_id)
    session.add(new_token)
    return new_token


@database_operation_wrapper
def delete_token(token: Token) -> None:
    session.delete(token)


@database_operation_wrapper
def get_tokens_by_user_id(user_id: int) -> list:
    tokens = session.query(Token).filter(Token.user_id == user_id)
    return tokens
