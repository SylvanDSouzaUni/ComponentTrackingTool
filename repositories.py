from models import User, Roles
from database import get_connection

def create_user(username, display_name, password_hash, role):
    with get_connection() as connection:
        connection.execute("insert into users (username, display_name, password_hash, role) values (?, ?, ?, ?)", (username, display_name, password_hash, role)
                           )

def select_user(username):
    with get_connection() as connection:
        row = connection.execute("select * from users where username = ?", (username,)).fetchone()

    return User(row["display_name"],
                row["username"],
                Roles(row["role"]),
                row["password_hash"]
                ) if row else None


