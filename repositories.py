from models import (User,
                    Roles,
                    Component,
                    Request,
                    AuditLogEntry,
                    ConditionStatus,
                    Order,
                    OrderStatus,
                    RequestStatus
                    )

from database import get_connection



#------------------------------------USERS-------------------------------------#
def return_user(username):
    with get_connection() as connection:
        row = connection.execute("select * from users where username = ?", (username,)).fetchone()

    return User(row["display_name"],
                row["username"],
                Roles(row["role"]),
                row["password_hash"]
                ) if row else None

def return_users():
    with get_connection() as connection:
        rows = connection.execute("select * from users").fetchall()

        return [
            User(
                row["display_name"],
                row["username"],
                Roles(row["role"]),
                row["password_hash"]
            )
            for row in rows
        ]

def create_user(username, display_name, password_hash, role):
    with get_connection() as connection:
        cursor = connection.execute("insert into users (username, display_name, password_hash, role) values (?, ?, ?, ?)", (username, display_name, password_hash, role)
                           )

    return cursor.rowcount > 0

def delete_user(username):
    with get_connection() as connection:
        cursor = connection.execute("delete from users where username = ?", (username,))

    return cursor.rowcount > 0

#----------------------------------COMPONENTS----------------------------------#

def return_component(sku):
    with get_connection() as connection:
        row = connection.execute("select * from components where sku = ?", (sku,)).fetchone()

    return Component(row["sku"],
                     row["component_name"],
                     row["unit"],
                     row["stock"],
                     row["min_stock"],
                     ConditionStatus(row["condition_status"])
                    ) if row else None

def return_components():
    with get_connection() as connection:
        rows = connection.execute("select * from components").fetchall()

    return [
        Component(
            row["sku"],
            row["component_name"],
            row["unit"],
            row["stock"],
            row["min_stock"],
            ConditionStatus(row["condition_status"])
        )
        for row in rows
    ]

def create_component(sku, name, unit, stock, min_stock, condition):

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO components (sku, component_name, unit, stock, min_stock, condition_status) VALUES (?, ?, ?, ?, ?, ?)",
            (sku, name, unit, stock, min_stock, condition)
        )

    return cursor.rowcount > 0

def delete_component(sku):

    with get_connection() as connection:
        cursor = connection.execute("delete from components where sku = ?", (sku,))

    return cursor.rowcount > 0

def update_component(update, values_for_update_list):

    with get_connection() as connection:
        cursor = connection.execute(update, values_for_update_list)

    return cursor.rowcount > 0

#------------------------------------ORDERS-------------------------------------#

def return_order(order_id):
    with get_connection() as connection:
        row = connection.execute(
                "SELECT * FROM orders WHERE order_id = ?", (order_id,)
            ).fetchone()

    return Order(row["order_id"],
                 row["sku"],
                 row["quantity"],
                 row["ordered_at"],
                 row["ordered_by"],
                 OrderStatus(row["status"]),
                 row["received_at"],
                 row["received_by"]
                 ) if row else None

def return_orders():
    with get_connection() as connection:
        rows = connection.execute("select * from orders").fetchall()

    return [
        Order(
            row["order_id"],
            row["sku"],
            row["quantity"],
            row["ordered_at"],
            row["ordered_by"],
            OrderStatus(row["status"]),
            row["received_at"],
            row["received_by"]
        )
        for row in rows
    ]

def create_order(sku, quantity, ordered_at, ordered_by, status):
    with get_connection() as connection:
        cursor = connection.execute(
            "insert into orders (sku, quantity, ordered_at, ordered_by, status, received_at, received_by) values (?,?,?,?,?,?,?)",
            (sku, quantity, ordered_at, ordered_by, status, None, None)
        )

    return cursor.rowcount > 0

def receive_order(order_id, sku, new_stock, received_at, received_by):
    with get_connection() as connection:
        cursor1 = connection.execute("update components set stock = ? where sku = ?", (new_stock, sku))
        cursor2 = connection.execute("update orders "
                           "set status = ?, "
                           "    received_at = ?, "
                           "    received_by = ? "        
                           "where order_id = ?",
                               (OrderStatus.RECEIVED.value,
                                received_at,
                                received_by,
                                order_id)
                               )

    return (cursor1.rowcount > 0) and (cursor2.rowcount > 0)


#-----------------------------------REQUESTS-------------------------------------#

def return_request(request_id):
    with get_connection() as connection:
        row = connection.execute(
            "select * from requests where request_id = ?",
            (request_id,)
        ).fetchone()

    if not row:
        return None

    request_state_str = row["request_state"] or RequestStatus.REQUESTED.value
    try:
        request_state = RequestStatus(request_state_str)
    except ValueError:
        request_state = RequestStatus.REQUESTED

    return Request(
        row["request_id"],
        row["component_name"],
        row["requested_by"],
        row["requested_at"],
        row["sku"],
        row["reviewed_by"],
        row["reviewed_at"],
        request_state
    )

def return_requests():
    with get_connection() as connection:
        rows = connection.execute("select * from requests").fetchall()

    requests = []
    for row in rows:
        request_state_str = row["request_state"] or RequestStatus.REQUESTED.value
        try:
            request_state = RequestStatus(request_state_str)
        except ValueError:
            request_state = RequestStatus.REQUESTED

        requests.append(
            Request(
                row["request_id"],
                row["component_name"],
                row["requested_by"],
                row["requested_at"],
                row["sku"],
                row["reviewed_by"],
                row["reviewed_at"],
                request_state
            )
        )

    return requests

def create_request(component_name, requested_by, requested_at, sku):
    with get_connection() as connection:
        cursor = connection.execute("insert into requests (component_name, requested_by, requested_at, sku, reviewed_by, reviewed_at, request_state) values (?, ?, ?, ?, ?, ?, ?)",
                           (component_name, requested_by, requested_at, sku, None, None, RequestStatus.REQUESTED.value)
                           )

    return cursor.rowcount > 0

def reject_request(request_id, reviewed_by, reviewed_at):
    with get_connection() as connection:
        cursor = connection.execute(
            "update requests "
            "set request_state = ?, reviewed_by = ?, reviewed_at = ? "
            "where request_id = ?",
            (RequestStatus.REJECTED.value, reviewed_by, reviewed_at, request_id)
        )

    return cursor.rowcount > 0

def accept_request(request_id, reviewed_by, reviewed_at):
    with get_connection() as connection:
        cursor = connection.execute(
            "update requests "
            "set request_state = ?, reviewed_by = ?, reviewed_at = ? "
            "where request_id = ?",
            (RequestStatus.ACCEPTED.value, reviewed_by, reviewed_at, request_id)
        )

    return cursor.rowcount > 0

#------------------------------------AUDITS--------------------------------------#


def create_audit_log(timestamp, actor, actor_role, action):
    with get_connection() as connection:
        cursor = connection.execute(
            "insert into audit_logs (timestamp, actor, actor_role, action) values (?, ?, ?, ?)",
            (timestamp, actor, actor_role, action)
        )

    return cursor.rowcount > 0


def return_audit_logs(limit=None):
    query = "select * from audit_logs order by audit_id desc"
    params = ()

    if limit is not None:
        query += " limit ?"
        params = (limit,)

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        AuditLogEntry(
            row["audit_id"],
            row["timestamp"],
            row["actor"],
            Roles(row["actor_role"]),
            row["action"]
        )
        for row in rows
    ]
