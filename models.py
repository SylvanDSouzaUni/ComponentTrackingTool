from enum import Enum
from typing import Optional


#ENUM DEFINITIONS
class Roles(Enum):
    WAREHOUSE = "WAREHOUSE"
    ENGINEER = "ENGINEER"
    ADMIN = "ADMIN"
    GUEST = "GUEST"

class ConditionStatus(Enum):
    FUNCTIONAL = "FUNCTIONAL"
    DAMAGED = "DAMAGED"
    EXPIRED = "EXPIRED"
    REPAIRING = "REPAIRING"
    OBSOLETE = "OBSOLETE"

class AvailabilityStatus(Enum):
    AVAILABLE = "AVAILABLE"
    CRITICAL = "CRITICAL"
    NO_STOCK = "NO_STOCK"

class OrderStatus(Enum):
    ORDERED = "ORDERED"
    RECEIVED = "RECEIVED"



#CLASS DEFINITIONS
class User:
    def __init__(self,
                 display_name    : str,
                 username        : str,
                 role            : Roles,
                 password_hash   : Optional[str] = None
                 ):

                    self.display_name   = display_name
                    self.username       = username
                    self.password_hash  = password_hash
                    self.role           = role

class Component:
    def __init__(self,
                 sku               : int,
                 component_name    : str,
                 unit              : str,
                 min_stock         : int,
                 stock             : int,
                 condition_status  : ConditionStatus
                 ):

                    self.sku                 = sku
                    self.component_name                = component_name
                    self.unit                = unit
                    self.min_stock           = min_stock
                    self.stock               = stock
                    self.condition_status    = condition_status
                    self.availability_status = AvailabilityStatus.NO_STOCK  if (stock == 0) \
                                                                            else AvailabilityStatus.CRITICAL if (stock < min_stock) \
                                                                            else AvailabilityStatus.AVAILABLE

class Order:
    def __init__(self,
                 order_id        : str,
                 sku             : int,
                 quantity        : int,
                 ordered_at      : float,
                 ordered_by      : str,
                 status          : OrderStatus,
                 received_at     : Optional[float] = None,
                 received_by     : Optional[str] = None
                 ):

                    self.order_id    = order_id
                    self.sku         = sku
                    self.quantity    = quantity
                    self.ordered_at  = ordered_at
                    self.ordered_by  = ordered_by
                    self.status      = status
                    self.received_at = received_at
                    self.received_by = received_by

class Request:
    def __init__(self,
                 request_id      : str,
                 quantity        : int,
                 name            : str,
                 requested_by    : str,
                 requested_at    : Optional[float] = None,
                 sku             : Optional[int] = None,
                 reviewed_by     : Optional[str] = None,
                 reviewed_at     : Optional[float] = None
                 ):

                    self.request_id = request_id
                    self.quantity = quantity
                    self.name = name
                    self.requested_by = requested_by
                    self.requested_at = requested_at
                    self.sku = sku
                    self.reviewed_by = reviewed_by
                    self.reviewed_at = reviewed_at

class AuditLogEntry:
    def __init__(self, audit_id: int, timestamp: float, actor: str, role: Roles, action: str):
        self.audit_id = audit_id
        self.timestamp = timestamp
        self.actor = actor
        self.actor_role = role
        self.action = action
