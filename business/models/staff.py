"""
Represents a staff member who manages orders, shipments, and inventory.
Staff accounts are linked to user logins and can process paid orders.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from storage.storage_manager import StorageManager

if TYPE_CHECKING:
    from business.models.account import Account
    from business.models.order import Order


class Staff:
    """Defines a store staff member with order management privileges."""

    def __init__(self, id: int, username: str, name: str):
        self.id = id
        self.username = username
        self.name = name
        self._account: Optional['Account'] = None  # linked account object

    # ---------------Account Collaboration----------------------------- #

    def set_account(self, account: 'Account') -> None:
        """Links this staff member to an Account (two-way link)."""
        self._account = account
        account.set_staff(self)

    def get_account(self) -> Optional['Account']:
        """Returns the linked Account, if any."""
        return self._account

    # ---------------Account Collaboration----------------------------- #

    def set_account(self, account: 'Account') -> None:
        """Links this staff member to an Account (two-way link)."""
        self._account = account
        account.set_staff(self)

    def get_account(self) -> Optional['Account']:
        """Returns the linked Account, if any."""
        return self._account

    # ---------------Staff Responsibilities----------------------------- #

    def list_pending_orders(self) -> List[Dict]:
        """Returns a list of all orders that are not yet shipped."""
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("status") != "SHIPPED"]

    def ship_paid_order(self, order_id: int, tracking_number: str) -> Dict:
        """
        Ships an order that has already been paid.
        Adds a shipment record and updates the order status.
        """
        from business.models.order import Order

        order = Order.find_by_id(order_id)
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        if order.status != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        shipment = order.ship_with(tracking_number)
        return {
            "success": True,
            "message": f"Order {order_id} shipped with tracking {tracking_number}",
            "shipment_id": shipment.id,
        }

    # -------------Persistence--------------------------------------------------- #

    def to_dict(self) -> Dict:
        """Converts this staff record to a dictionary for storage."""
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Staff":
        """Recreates a Staff object from stored data."""
        return Staff(
            id=data["id"],
            username=data["username"],
            name=data["name"],
        )

    @staticmethod
    def add(username: str, name: str) -> "Staff":
        """Creates and saves a new staff record."""
        s = StorageManager()
        record = s.add("staff", {"username": username, "name": name})
        return Staff.from_dict(record)

    @staticmethod
    def find_by_id(staff_id: int) -> Optional["Staff"]:
        """Finds a staff record by ID."""
        s = StorageManager()
        row = s.find_by_id("staff", staff_id)
        return Staff.from_dict(row) if row else None

    @staticmethod
    def list_orders_by_status(status: str) -> List[Dict]:
        """Lists all orders that match a given status."""
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("status") == status]

    def __repr__(self):
        return f"Staff(id={self.id}, username={self.username}, name={self.name})"
