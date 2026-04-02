from abstractions.db import get_db_connection

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db_connection()
    users = conn.execute("""
        SELECT * FROM users
        ORDER BY id
    """).fetchall()
    conn.close()
    return users

def update_user_role(user_id, new_role):
    conn = get_db_connection()
    conn.execute("""
        UPDATE users
        SET role = ?
        WHERE id = ?
    """, (new_role, user_id))
    conn.commit()
    conn.close()