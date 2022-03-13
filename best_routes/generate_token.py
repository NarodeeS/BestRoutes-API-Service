import random
import string


def generate_token(user_id: str) -> str:
    return str(user_id) + ":" + ''.join(random.SystemRandom()
                                        .choice(string.ascii_letters + string.digits)
                                        for _ in range(25))
