from best_routes.database import get_tokens_by_user_id


def check_login(token: str) -> bool:
    user_id = int(token.split(":")[0])
    user_tokens = get_tokens_by_user_id(user_id)
    for user_token in user_tokens:
        if user_token.value == token:
            return True
    return False
