from database import create_schema, get_connection
from authentication import create_starting_admin, login, create_user


def main_loop():

    create_schema()
    create_starting_admin()

    while True:
        print("[CONSOLE] PLEASE LOG IN WITH YOUR CREDENTIALS")
        user = None
        while not user:
            user = login()

if __name__ == "__main__":
    main_loop()
