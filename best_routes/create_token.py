import random
import string
from .database import session
from .models import Token


def create_token(user_id: str) -> Token:
    new_token_value = str(user_id) + ":" + ''.join(random.SystemRandom()
                                                   .choice(string.ascii_letters + string.digits)
                                                   for _ in range(25))
    new_token = Token(value=new_token_value, user_id=user_id)
    session.add(new_token)
    session.commit()
    session.rollback()
    return new_token
