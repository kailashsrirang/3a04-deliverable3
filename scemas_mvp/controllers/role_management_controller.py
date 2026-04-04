from abstractions.user_model import get_all_users, update_user_role
from abstractions.log_model import log_action

def fetch_all_users():
    return get_all_users()

def change_user_role(user_id, new_role):
    update_user_role(user_id, new_role)
    log_action("UPDATE_ROLE", f"User ID {user_id} role changed to {new_role}")