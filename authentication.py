from database import get_connection
from repositories import (create_user,
                          return_user)
from models import (Roles,
                    User)

import hashlib, secrets


#Structure to store actions that each role is permitted to do
PERMISSIONS = {
    Roles.ADMIN: {
        "CREATE_COMPONENT",
        "UPDATE_COMPONENT",
        "DELETE_COMPONENT",
        "LIST_COMPONENTS",
        "LIST_LOW_STOCK",
        "CREATE_USER",
        "DELETE_USER",
        "LIST_USERS",
        "CREATE_ORDER",
        "RECEIVE_ORDER",
        "LIST_ORDERS",
        "CREATE_REQUEST",
        "ACCEPT_REQUEST",
        "REJECT_REQUEST",
        "LIST_REQUESTS",
        "LIST_AUDIT_LOGS",
        "ADMIN_ONLY"
    },
    Roles.ENGINEER: {
        "LIST_COMPONENTS",
        "LIST_LOW_STOCK",
        "CREATE_REQUEST",
        "LIST_REQUESTS",
        "CREATE_ORDER"
        "LIST_ORDERS"
    },
    Roles.WAREHOUSE: {
        "LIST_COMPONENTS",
        "LIST_LOW_STOCK",
        "CREATE_ORDER",
        "RECEIVE_ORDER",
        "LIST_ORDERS",
    }
}

#Funciton which checks if a user is permitted to complete an action.
def permission_checker(user, action):
    action = str(action).strip().upper()
    if action in PERMISSIONS.get(user.role, set()):
        return True
    else:
        return False

#Function which creates a starting admin if there are no users in the user table
def create_starting_admin():
    with get_connection() as connection:
        row = connection.execute("SELECT count(*) as total FROM users").fetchone()
    if row["total"] == 0:
        create_user("admin", "First Admin", hash_password("admin123"), Roles.ADMIN.value)

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

#Function to log into system.
def login():
    username = input("Username: ")
    password = input("Password: ")
    selection = return_user(username)
    if not selection:
        print("[ERROR] User not found \n")
        return None
    if not check_password(password, selection.password_hash):
        print("[ERROR] Incorrect Password \n")
        return None
    session_user = User(selection.display_name, selection.username, selection.role)
    print(f"[CONSOLE] Hi {session_user.display_name}! Welcome to the Component Tracking Tool")
    return session_user
