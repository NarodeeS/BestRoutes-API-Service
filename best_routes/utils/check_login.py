from best_routes.models import Token
from best_routes.database import session


def check_login(token: str) -> bool:
    user_id = token.split(":")[0]
    user_tokens = session.query(Token).filter(Token.user_id == user_id)
    for user_token in user_tokens:
        if user_token.value == token:
            return True
    return False
