from database import get_connection
from repositories import (create_user,
                          select_user)
from models import (Roles,
                    User)

import hashlib, secrets
from sqlite3 import IntegrityError


#Function to hash passwords
def hash_password(password):
    salt = secrets.token_hex(16)
    hashable_input = salt + password
    hash_result = hashlib.sha256(hashable_input.encode()).hexdigest()
    return f"{salt}${hash_result}"

#Function to verify passwords on login attempts
def check_password(password_attempt, stored):
    try:
        salt, stored_hash = stored.split("$", 1)
    except ValueError:
        return False
    test = hashlib.sha256((salt + password_attempt).encode()).hexdigest()

    if test == stored_hash:
        return True
    else:
        return False

def create_starting_admin():
    with get_connection() as connection:
        row = connection.execute("SELECT count(*) as total FROM users").fetchone()
    if row["total"] == 0:
        create_user("admin", "First Admin", hash_password("admin123"), Roles.ADMIN.value)


def login():
    username = input("Username: ")
    password = input("Password: ")
    selection = select_user(username)
    if not selection:
        print("User not found")
        return None
    if not check_password(password, selection.password_hash):
        print("Incorrect Password")
        return None
    session_user = User(selection.display_name, selection.username, selection.role)
    print("Hi {name}! Welcome to the Component Tracking Tool".format(name=session_user.display_name))
    return session_user
