from abstractions.user_model import get_user_by_username
from abstractions.log_model import log_action

def login_user(username):
    username = username.strip().lower()
    user = get_user_by_username(username)

    if not user:
        return None

    log_action("LOGIN", f"{username} logged in")
    return user