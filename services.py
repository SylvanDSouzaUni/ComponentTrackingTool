import time
from sqlite3 import IntegrityError

import repositories

from validation import (validation_for_integer_input,
                        validation_for_string_input,
                        validation_for_non_empty_input,
                        validate_actor)

from authentication import hash_password

from models import ConditionStatus, Roles, OrderStatus



def audit(actor_username, action):

    try:

        user = repositories.return_user(actor_username)
        if user is None:
            print(f"[ERROR] Audit failed: user '{actor_username}' does not exist.")
            return

        created = repositories.create_audit_log(
            time.time(),
            actor_username,
            user.role.value,
            action
        )

        if not created:
            print("[ERROR] Failed to create audit log entry.")

    except IntegrityError as e:
        print(f"[ERROR] Audit failed due to database constraint: {e}")

    except Exception as e:
        print(f"[ERROR] Audit failed: {e}")


#----------------------------------------------------------COMPONENT SERVICES----------------------------------------------------------#
def create_new_component(sku, name, unit, stock, min_stock, actor):

    try:

        validate_actor(actor)
        sku = validation_for_integer_input(sku, "sku")
        name = validation_for_string_input(name, "name")
        unit = validation_for_string_input(unit, "unit")
        stock = validation_for_integer_input(stock, "stock")
        min_stock = validation_for_integer_input(min_stock, "min_stock")
        condition =  ConditionStatus.FUNCTIONAL.value

        created = repositories.create_component(sku, name, unit, stock, min_stock, condition)

        if created:
            print(f"[CONSOLE] Component ({sku}) successfully created. \n")
            audit(actor, f'Created a new component: SKU = {sku}, NAME = {name}.')

    except IntegrityError as e:
        msg = str(e).lower()

        if "unique" in msg or "primary key" in msg:
            print(f"[ERROR] SKU must be unique. A component with this sku ({sku}) already exists.\n")
        elif "check constraint" in msg or "check" in msg:
            print(f"[ERROR] Invalid component values (failed a CHECK constraint): {e}\n")
        else:
            print(f"[ERROR] Database constraint failed: {e}\n")

    except Exception as e:
        print(f"[ERROR] Failed to add component: {e} \n")

def delete_component(sku, actor):
    try:

        validate_actor(actor)
        sku = validation_for_integer_input(sku, "sku")

        deleted = repositories.delete_component(sku)

        if deleted:
            print(f"[CONSOLE] Component {sku} deleted. \n")
            audit(actor, f'Deleted a component: SKU = {sku}.')
        else:
            print(f"[ERROR] Component {sku} not found. \n")

    except Exception as e:
        print(f"[ERROR] Failed to delete component: {e} \n")

def list_components():
    try:
        components = repositories.return_components()

        if not components:
            print(f"[ERROR] No components found.")
            input("\n Press ENTER to continue...")
            return


        table = ["SKU        | "
                 "NAME                 | "
                 "UNIT       | "
                 "MINIMUM STOCK  | "
                 "STOCK   | "
                 "CONDITION        |" ,
                 "-" * 94
                 ]

        for component in components:
            table.append(f"{component.sku:<8}   | "
                         f"{component.component_name:<20} | "
                         f"{component.unit:<5}     | "
                         f"{component.min_stock:<3}            | "
                         f"{component.stock:<5}   | "
                         f"{component.condition_status.value:<5}         |"
                         )

        print("\n".join(table))
        input("\n Press ENTER to continue...")


    except Exception as e:
        print(f"Failed to list components. [ERROR: {e}]")

def update_component(actor, sku, name=None, unit=None, min_stock=None, stock=None, condition=None):

    try:

        validate_actor(actor)
        sku = validation_for_integer_input(sku, "SKU")

        update_list = []
        values_for_update_list = []
        errors = []

        if stock is not None:
            try:
                stock = validation_for_integer_input(stock, "STOCK")
                update_list.append("stock = ?")
                values_for_update_list.append(stock)
            except Exception as e:
                errors.append(str(e))

        if min_stock is not None:
            try:
                min_stock = validation_for_integer_input(min_stock, "MIN_STOCK")
                update_list.append("min_stock = ?")
                values_for_update_list.append(min_stock)
            except Exception as e:
                errors.append(str(e))

        if unit is not None:
            try:
                unit = validation_for_string_input(unit, "UNIT")
                update_list.append("unit = ?")
                values_for_update_list.append(unit)
            except Exception as e:
                errors.append(str(e))

        if name is not None:
            try:
                name = validation_for_string_input(name, "NAME")
                update_list.append("component_name = ?")
                values_for_update_list.append(name)
            except Exception as e:
                errors.append(str(e))

        if condition is not None:
            mapping = {
                1: ConditionStatus.FUNCTIONAL.value,
                2: ConditionStatus.DAMAGED.value,
                3: ConditionStatus.EXPIRED.value,
                4: ConditionStatus.REPAIRING.value,
                5: ConditionStatus.OBSOLETE.value
            }
            if condition in mapping:
                update_list.append("condition_status = ?")
                values_for_update_list.append(mapping[condition])
            else:
                errors.append("Invalid condition selection.")

        if errors:
            raise ValueError("; ".join(errors))

        if not update_list:
            print("No fields to update.")
            return

        values_for_update_list.append(sku)
        update = f"update components set {', '.join(update_list)} where sku = ?"

        updated = repositories.update_component(update, values_for_update_list)

        if updated:
            print(f"[Console] Component ({sku}) successfully updated. \n")
            audit(actor, f'Updated a component: SKU = {sku}.')
        else:
            print(f"[ERROR] Component ({sku}) not found. \n")

    except Exception as e:
        print(f"[ERROR] Failed to update component: {e} \n")
#------------------------------------------------------------USER SERVICES-------------------------------------------------------------#
def create_new_user(actor, username, name, password, role):

    try:

        validate_actor(actor)
        username = validation_for_string_input(username, "USERNAME")
        name = validation_for_string_input(name, "NAME")
        role = validation_for_non_empty_input(role, "ROLE")

        if role.upper() not in [role.value for role in Roles]:
            print("[ERROR] You have provided an invalid role. Please choose from: ADMIN, ENGINEER, WAREHOUSE")
            return

        created = repositories.create_user(username, name, hash_password(password), role.upper())

        if created:
            print(f"[Console] User {username} successfully created. \n")
            audit(actor, f'Created a new user: USERNAME = {username}, NAME = {name}.')
        else:
            print(f"[ERROR] Could not create User ({username}). \n")

    except IntegrityError as e:
        msg = str(e).lower()
        if "unique" in msg or "primary key" in msg:
            print(f"[ERROR] Username must be unique. '{username}' already exists.\n")
        elif "check" in msg:
            print(f"[ERROR] Invalid user values (failed a CHECK constraint): {e}\n")
        else:
            print(f"[ERROR] Database constraint failed: {e}\n")

    except Exception as e:
        print(f"[ERROR] Failed to create user: {e} \n")

def delete_user(actor, username):

    try:

        validate_actor(actor)
        username = validation_for_string_input(username, "USERNAME")
        deleted = repositories.delete_user(username)

        if deleted:
            print(f"[Console] User {username} successfully deleted. \n")
            audit(actor, f'Deleted a user: USERNAME = {username}.')
        else:
            print(f"[ERROR] User {username} not found. \n")

    except Exception as e:
        print(f"[ERROR] Failed to delete user: {e} \n")

def list_users():

    try:

        users = repositories.return_users()

        if not users:
            print(f"\n[ERROR] No users found.")
            input("[CONSOLE] Press ENTER to continue...")
            return


        table = ["USERNAME                 | "
                 "NAME                 | "
                 "ROLE           | "
                 "PASSWORD HASH                                                                                         |" ,
                 "-" * 170
                 ]

        for user in users:
            table.append(f"{user.username:<20}     | "
                         f"{user.display_name:<20} | "
                         f"{user.role.value:<10}     | "
                         f"{user.password_hash:<3}     |"
                         )

        print("\n".join(table))
        input("\n Press ENTER to continue...")


    except Exception as e:
        print(f"Failed to list users. [ERROR: {e}]")

#-----------------------------------------------------------ORDER SERVICES-------------------------------------------------------------#

def create_order(actor, sku, quantity, ordered_by):

    try:

        validate_actor(actor)
        sku = validation_for_integer_input(sku, "SKU")
        quantity = validation_for_integer_input(quantity, "QUANTITY")
        ordered_by = validation_for_string_input(ordered_by, "ORDERED_BY")

        if quantity <= 0:
            print("[ERROR] Quantity must be greater than 0.")
            return

        component = repositories.return_component(sku)
        if component is None:
            print(f"[ERROR] Cannot place order: component not found with SKU: {sku}")
            return

        user = repositories.return_user(ordered_by)
        if user is None:
            print(f"[ERROR] Cannot place order: user '{ordered_by}' does not exist.")
            return

        timestamp = time.time()
        ordered = repositories.create_order(sku, quantity, timestamp, ordered_by, OrderStatus.ORDERED.value)

        if ordered:
            print(f"[CONSOLE] Order successfully placed: {sku} ({component.component_name}) x{quantity}. \n")
            audit(actor, f"Created order for {component.component_name} x{quantity}.")
        else:
            print("[ERROR] Order failed")

    except IntegrityError as e:
        msg = str(e).lower()
        if "foreign key" in msg:
            print(f"[ERROR] Order failed due to foreign key constraint: {e}")
        elif "check" in msg:
            print(f"[ERROR] Order failed due to invalid values (CHECK constraint): {e}")
        else:
            print(f"[ERROR] Database constraint failed: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to create order: {e} \n")

def receive_order(actor, order_id, received_by):

    try:

        validate_actor(actor)
        order_id = validation_for_integer_input(order_id, "ORDER_ID")
        received_by = validation_for_string_input(received_by, "RECEIVED_BY")


        user = repositories.return_user(received_by)
        if user is None:
            print(f"[ERROR] Cannot receive order: user '{received_by}' does not exist.")
            return

        order = repositories.return_order(order_id)
        if not order:
            print(f"[ERROR] Order not found with ID: {order_id} \n")
            return

        component = repositories.return_component(order.sku)
        if not component:
            print(f"[ERROR] Component not found with SKU: {order.sku} \n")
            return

        if order.status == OrderStatus.RECEIVED:
            print(f"[ERROR] Order #{order_id} is already {order.status.value}. \n")
            return

        print(f"====ORDER INFO===="
              f"\n Order: #{order.order_id}"
              f"\n Name: {component.component_name}"
              f"\n SKU: {component.sku}"
              f"\n Quantity of order: {order.quantity}"
              )

        confirmation = input(
            "[CONSOLE] Press ENTER to confirm the arrival of this order, else input CANCEL to cancel: ").strip().lower()

        if confirmation == "cancel":
            print("[CONSOLE] Successfully cancelled.")
            return

        stock = component.stock
        new_stock = stock + order.quantity
        received = repositories.receive_order(order_id, component.sku, new_stock, time.time(), received_by)

        if received:
            print(f"[CONSOLE] Order #{order_id} has been received successfully. Stock updated from {stock} to {new_stock}.")
            audit(actor, f'Received order #{order_id} for {component.component_name}.')
            return
        else:
            print(f"[ERROR] Failed to receive order")
            return

    except IntegrityError as e:
        msg = str(e).lower()
        if "foreign key" in msg:
            print(f"[ERROR] Receive failed due to foreign key constraint: {e}")
        elif "check" in msg:
            print(f"[ERROR] Receive failed due to invalid values (CHECK constraint): {e}")
        else:
            print(f"[ERROR] Database constraint failed: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to receive order: {e} \n")

def list_orders():

    try:

        orders = repositories.return_orders()

        if not orders:
            print(f"\n[ERROR] No orders found.")
            input(f"CONSOLE] Press ENTER to continue...")
            return

        table = ["ORDER ID            | "
                 "SKU                 | "
                 "QUANTITY        | "
                 "ORDERED BY           | "
                 "ORDERED AT      |" 
                 "STATUS              | "
                 "RECEIVED BY          | "
                 "RECEIVED AT          |",
                 "-" * 170
                 ]

        for order in orders:

            received_by = order.received_by if order.received_by else "PENDING..."
            received_at = order.received_at if order.received_at else "N/A"

            table.append(f"{order.order_id:<20}     | "
                         f"{order.sku:<18} | "
                         f"{order.quantity:<14} | "
                         f"{order.ordered_by:<18}     |"
                         f"{order.ordered_at:<10}     |"
                         f"{order.status.value:<18}     |"
                         f"{received_by:<18}     |"
                         f"{received_at:<18}     |"
                         )

        print("\n".join(table))
        input("\n Press ENTER to continue...")

    except Exception as e:
        print(f"[ERROR] Failed to list orders: {e} \n")

#-----------------------------------------------------COMPONENT REQUESTS SERVICES------------------------------------------------------#

def create_request(actor, requested_by, component_name, sku = None):

    try:

        validate_actor(actor)

        #Basic normalisation as validation will occur in approve request instead
        requested_by = validation_for_string_input(requested_by, "REQUESTED_BY")
        component_name = validation_for_string_input(component_name, "COMPONENT NAME")
        sku = (str(sku).strip()) if sku is not None else None

        # FK safety: user must exist
        user = repositories.return_user(requested_by)
        if user is None:
            print(f"[ERROR] Cannot create request: user '{requested_by}' does not exist.")
            return

        created = repositories.create_request(component_name, requested_by, time.time(), sku)

        if created:
            print(f"[CONSOLE] Successfully created request")
            audit(actor, f'Created a new request: SKU = {sku}, NAME = {component_name}.')
        else:
            print(f"[ERROR] Failed to create request")

    except IntegrityError as e:
        msg = str(e).lower()
        if "foreign key" in msg:
            print(f"[ERROR] Request failed due to foreign key constraint: {e}")
        elif "check" in msg:
            print(f"[ERROR] Request failed due to invalid values (CHECK constraint): {e}")
        else:
            print(f"[ERROR] Database constraint failed: {e}")

    except Exception as e:
         print(f"[ERROR] Failed to create request: {e} \n")

def accept_request(actor, request_id, reviewed_by):

    try:

        validate_actor(actor)
        request_id = validation_for_integer_input(request_id, "REQUEST ID")
        reviewed_by = validation_for_string_input(reviewed_by, "REVIEWED BY")

        # FK safety: reviewer must exist
        reviewer = repositories.return_user(reviewed_by)
        if reviewer is None:
            print(f"[ERROR] Cannot accept request: reviewer '{reviewed_by}' does not exist.")
            return

        request = repositories.return_request(request_id)
        if not request:
            print(f"[ERROR] Request not found with ID: {request_id} \n")
            return

        sku = request.sku
        component_name = request.component_name


        print("\n=====CHOSEN REQUEST=====")
        print(f"REQUEST ID: {request_id}")
        print(f"SKU: {sku}")
        print(f"NAME: {component_name}")

        # Offers ADMIN the choice to edit any fields of request before approving
        choice = input("Edit any fields before approval (Y/N)").strip().lower()

        if choice == "y":

            new_sku = input(f"SKU [{sku or ''}: ")
            if new_sku:
                sku = validation_for_integer_input(new_sku, "SKU")

            new_item_name = input(f"NAME [{component_name or ''}]: ")
            if new_item_name:
                component_name = validation_for_string_input(new_item_name, "NAME")

        # Ensures Default values are set for fields that require it
        sku = validation_for_integer_input(sku or input("SKU (required): "), "SKU")
        component_name = validation_for_string_input(component_name or input("NAME (required): "), "NAME")

        stock = validation_for_integer_input(input("\nSTOCK (required): "), "STOCK")
        min_stock = validation_for_integer_input(input("\nMINIMUM STOCK (required): "), "STOCK")
        unit = validation_for_string_input(input("\nUNIT (required): "), "UNIT")

        created = repositories.create_component(sku, component_name, unit, stock, min_stock, ConditionStatus.FUNCTIONAL.value)
        if not created:
            print("[ERROR] Failed to create component, request not accepted.")
            return

        accepted = repositories.accept_request(
            request_id,
            reviewed_by,
            time.time()
        )
        if accepted:
            print(f"[CONSOLE] Request #{request_id} accepted successfully. {component_name} added to COMPONENTS.")
            audit(actor, f'Accepted request #{request_id} for {component_name}.')
        else:
            print(f"[ERROR] Failed to mark request #{request_id} as accepted.")

    except IntegrityError as e:
        msg = str(e).lower()
        if "unique" in msg or "primary key" in msg:
            print("[ERROR] Component SKU must be unique - an item with this SKU already exists.")
        elif "foreign key" in msg:
            print(f"[ERROR] Accept failed due to foreign key constraint: {e}")
        elif "check" in msg:
            print(f"[ERROR] Accept failed due to CHECK constraint: {e}")
        else:
            print(f"[ERROR] Database constraint failed: {e}")

    except Exception as e:
        print(f"Failed to approve item: [ERROR]: {e}")

def reject_request(actor, request_id, reviewed_by):

    try:

        validate_actor(actor)
        request_id = validation_for_integer_input(request_id, "REQUEST ID")
        reviewed_by = validation_for_string_input(reviewed_by, "REVIEWED BY")

        reviewer = repositories.return_user(reviewed_by)
        if reviewer is None:
            print(f"[ERROR] Cannot reject request: reviewer '{reviewed_by}' does not exist.")
            return

        request = repositories.return_request(request_id)
        if not request:
            print(f"[ERROR] Request not found with ID: {request_id} \n")
            return

        sku = request.sku
        component_name = request.component_name

        print("\n=====CHOSEN REQUEST=====")
        print(f"REQUEST ID: {request_id}")
        print(f"SKU: {sku}")
        print(f"NAME: {component_name}")

        confirmation = input(
            f"\nYou are about to reject a request (Request ID: {request_id}). Press ENTER to continue or reply CANCEL to cancel: ").strip().lower()

        if confirmation == "cancel":
            print(f"[CONSOLE] Rejection of request has been cancelled.")
            return

        rejection = repositories.reject_request(
            request_id,
            reviewed_by,
            time.time()
        )
        if rejection:
            print(f"[CONSOLE] Request #{request_id} has successfully been rejected.")
            audit(actor, f'Rejected request #{request_id}.')
        else:
            print(f"[ERROR] Request #{request_id} was not found.")

    except IntegrityError as e:
        msg = str(e).lower()
        if "foreign key" in msg:
            print(f"[ERROR] Reject failed due to foreign key constraint: {e}")
        elif "check" in msg:
            print(f"[ERROR] Reject failed due to CHECK constraint: {e}")
        else:
            print(f"[ERROR] Database constraint failed: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to reject request: [ERROR]: {e}")

def list_requests():

    try:

        requests = repositories.return_requests()

        if not requests:
            print(f"\n[ERROR] No requests found.")
            input(f"CONSOLE] Press ENTER to continue...")
            return

        table = ["ID                 | "
                 "COMPONENT NAME        | "
                 "SKU             |"
                 "REQUESTED BY           | "
                 "REQUESTED AT      |" 
                 "REVIEWED BY           | "
                 "REVIEWED AT           | "
                 "REQUEST STATE          |",
                 "-" * 170
                 ]

        for request in requests:

            component_name = request.component_name if request.component_name else "X"
            sku = request.sku if request.sku is not None else "X"
            reviewed_by = request.reviewed_by if request.reviewed_by else "PENDING..."
            reviewed_at = request.reviewed_at if request.reviewed_at else "N/A"

            table.append(f"{request.request_id:<20}     | "
                         f"{component_name:<20} | "
                         f"{sku:<10}     | "
                         f"{request.requested_by:<10}     |"
                         f"{request.requested_at:<10}     |"
                         f"{reviewed_by:<10}     |"
                         f"{reviewed_at:<10}     |"
                         f"{request.request_state.value:<10}     |"
                         )

        print("\n".join(table))
        input("\n Press ENTER to continue...")

    except Exception as e:
        print(f"[ERROR] Failed to list requests: {e} \n")


