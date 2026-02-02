from database import create_schema, get_connection
from authentication import create_starting_admin, login, create_user
from menu import main_menu

def main_loop():

    create_schema()
    create_starting_admin()

    while True:
        print("[CONSOLE] PLEASE LOG IN WITH YOUR CREDENTIALS")
        session_user = None
        while not session_user:
            session_user = login()

        current_status = main_menu(session_user)

        if current_status == "logged out":
            continue
        elif current_status == "exit":
            break


if __name__ == "__main__":
    main_loop()
