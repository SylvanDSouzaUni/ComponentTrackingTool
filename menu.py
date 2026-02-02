from services import (create_new_component,
                      delete_component,
                      list_components,
                      update_component,
                      list_low_stock_components,
                      create_new_user,
                      delete_user,
                      list_users,
                      create_order,
                      receive_order,
                      list_orders,
                      create_request,
                      accept_request,
                      reject_request,
                      list_requests,
                      list_audit_logs)

from authentication import permission_checker

def main_menu(user):
    print("=== Welcome to the Component Tracking System ===")
    while True:
        print("\n=====MAIN MENU=====")
        print("Choose an option:")
        print("1) List components")
        print("2) Update component")
        print("3) Submit a component request")
        print("4) View Low Stock items")
        print("5) Place Order")
        print("6) Receive Order")
        print("7) List Orders")


        print("9) Admin actions")
        print("0) Log out")
        print("*) Exit")

        choice = input("Enter your choice: ").strip()

        #List components
        if choice == "1":

            #Check permissions
            if not permission_checker(user, "LIST_COMPONENTS"):
                print("You do not have permission to do this.")
                continue

            #Perform action
            list_components()

        #Update components
        elif choice == "2":

            #Check permissions
            if not permission_checker(user, "UPDATE_COMPONENT"):
                print("You do not have permission to do this.")
                continue

            #Perform action
            sku = input("SKU to update: ").strip()
            new_name = input("New name (blank = unchanged): ").strip() or None
            new_unit = input("New unit (blank = unchanged): ").strip() or None
            new_min = input("New min level (blank = unchanged): ").strip() or None
            new_stock = input("New stock (blank = unchanged): ").strip() or None
            new_condition = input("New condition "
                                  "(1: FUNCTIONAL"
                                  "\n 2: DAMAGED"
                                  "\n 3: EXPIRED"
                                  "\n 4: REPAIRING"
                                  "\n 5: OBSOLETE"
                                  "\n blank = unchanged): "
                                  ).strip() or None


            new_condition = int(new_condition) if new_condition is not None else None


            update_component(user.username, sku, new_name, new_unit, new_min, new_stock, new_condition)

        #Submit component request
        elif choice == "3":

            #Check permissions
            if not permission_checker(user, "CREATE_REQUEST"):
                print("You do not have permission to do this.")
                continue

            #Perform action
            component = input("Component to be requested: ")
            sku = input("You may suggest an SKU for this component: ")

            create_request(user.username, user.username, component, sku)

        #View low-stock items
        elif choice == "4":

            #Check permissions
            if not permission_checker(user, "LIST_LOW_STOCK"):
                print("You do not have permission to do this.")
                continue

            # Perform action
            list_low_stock_components()

        elif choice == "5":

            #Check permissions
            if not permission_checker(user, "CREATE_ORDER"):
                print("You do not have permission to do this.")
                continue

            # Perform action
            sku = input("SKU to be ordered: ")
            quantity = input("Quantity to be ordered: ")

            create_order(user.username, sku, quantity, user.username)

        elif choice == "6":

            #Check permissions
            if not permission_checker(user, "RECEIVE_ORDER"):
                print("You do not have permission to do this.")
                continue

            # Perform action
            order_id = input("Enter the Order ID of the order you have received: ")
            receive_order(user.username, order_id, user.username)

        elif choice == "7":

            # Check permissions
            if not permission_checker(user, "LIST_ORDERS"):
                print("You do not have permission to do this.")
                continue

            # Perform action
            list_orders()

        elif choice == "9":
            #Check permissions
            if not permission_checker(user, "ADMIN_ONLY"):
                print("You do not have permission to do this.")
                continue

            # Perform action
            admin_only_menu(user)

        #Log out
        elif choice == "0":
            print("Logging out...")
            return "logged out"

        #Exit
        elif choice == "*":
            print("Exiting..")
            return "exit"

        #Failsafe
        else:
            print("Invalid choice. Please pick the number corresponding to your desired action.")


#Seperate menu system for admin exclusive actions
def admin_only_menu(user):
    while True:
        print("\n=====ADMIN MANAGEMENT=====")

        print("1) Create component")
        print("2) Delete component")
        print("3) List audit logs")
        print("4) Manage users")
        print("5) Manage requests")

        print("0) Back")

        choice = input("Enter your choice: ").strip()


        #Create component
        if choice == "1":

            sku = input("SKU: ").strip()
            name = input("Name: ").strip()
            unit = input("Unit (default 'each'): ").strip() or "each"
            stock = input("Current stock (default 0): ").strip() or "0"
            min_level = input("Minimum level for Stock (default 0): ").strip() or "0"

            create_new_component(sku, name, unit, stock, min_level, user.username)



        #Delete component
        elif choice == "2":
            # Remove item
            sku = input("SKU to remove: ").strip()

            delete_component(sku, user.username)

        #List audit logs
        elif choice == "3":
            list_audit_logs()

        #Manage Users
        elif choice == "4":
            user_management_menu(user)

        #Manage Requests
        elif choice == "5":
            request_management_menu(user)


        #Back
        elif choice == "0":
            print("\nReturning to Main Menu...")
            return

        # Failsafe
        else:
            print("Invalid choice. Please pick the number corresponding to your desired action.")

#Seperate menu system for admin to handle users
def user_management_menu(user):
    while True:
        print("\n=====MANAGE USERS=====")
        print("1) Create user")
        print("2) Delete user")
        print("3) List user information")

        print("0) Back ")
        choice = input("Enter your choice: ").strip()

        #Add user to table
        if choice == "1":
            username = input("Username to add: ").strip()
            password = input("Password of new account: ").strip()
            role = input("Role of new account: ").strip()
            name = input("Name of account holder: ").strip()
            create_new_user(user.username, username, name, password, role)

        #Remove user from table
        elif choice == "2":
            username = input("Username to delete: ").strip()
            delete_user(user.username, username)

        #List user info
        elif choice == "3":
            #List all user info
            list_users()

        #Back
        elif choice == "0":
            print("\nReturning to Admin Menu...")
            return

        #Failsafe
        else:
            print("Invalid choice. Please pick the number corresponding to your desired action.")

#Seperate menu system for admin to handle requests
def request_management_menu(user):
    while True:
        print("\n=====MANAGE REQUESTS=====")
        print("1) Approve request")
        print("2) Reject request")
        print("3) List requests")

        print("0) Back ")
        choice = input("Enter your choice: ").strip()

        #Approve request
        if choice == "1":
            request_id = input("Request ID of request to approve: ").strip()
            accept_request(user.username, request_id, user.username)

        #Reject request
        elif choice == "2":
            request_id = input("Request ID of request to reject: ").strip()
            reject_request(user.username, request_id, user.username)

        #List requests
        elif choice == "3":
            list_requests()

        #Back
        elif choice == "0":
            print("\nReturning to Admin Menu...")
            return

        #Failsafe
        else:
            print("Invalid choice. Please pick the number corresponding to your desired action.")
