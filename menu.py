import services


def main_menu():
    print("=== Welcome to the Component Tracking System ===")

    while True:
        print("\n=====MAIN MENU=====")
        print("Choose an option:")
        print("1) List Components")


        print("9) Admin Actions")
        print("0) Log out")
        print("*) Exit")

        choice = input("Enter your choice: ").strip()
