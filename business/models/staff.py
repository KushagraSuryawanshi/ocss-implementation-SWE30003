"""
File: staff.py
Layer: Business Logic
Component: Domain Model - Staff
Description:
    Represents staff who manage inventory and shipments.

Refactor notes (non-breaking):
    - Added domain-action helpers Staff can perform directly:
        * list_pending_orders()
        * ship_paid_order(order_id, tracking_number)
    - Existing static API preserved.
"""
from typing import Dict, List
from storage.storage_manager import StorageManager
from business.models.order import Order

class Staff:
    def __init__(self, id: int, username: str, name: str):
        self.id = id
        self.username = username
        self.name = name

    # ---------- New collaboration helpers ----------
    def list_pending_orders(self) -> List[Dict]:
        """List all orders not yet shipped."""
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("status") != "SHIPPED"]

    def ship_paid_order(self, order_id: int, tracking_number: str) -> Dict:
        """Ship an order that has been paid."""
        order = Order.find_by_id(order_id)
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        if order.status != "PAID":
            return {"success": False, "message": "Order not yet paid"}
        shipment = order.ship_with(tracking_number)
        return {
            "success": True,
            "message": f"Order {order_id} shipped with tracking {tracking_number}",
            "shipment_id": shipment.id
        }

    # ---------- Existing API ----------
    def to_dict(self) -> Dict:
        """Serialize staff member to dictionary."""
        return {"id": self.id, "username": self.username, "name": self.name}

    @staticmethod
    def from_dict(data: Dict) -> "Staff":
        """Create Staff object from dictionary."""
        return Staff(id=data["id"], username=data["username"], name=data["name"])

    @staticmethod
    def add(username: str, name: str) -> "Staff":
        """Add a new staff member to storage."""
        s = StorageManager()
        rec = s.add("staff", {"username": username, "name": name})
        return Staff.from_dict(rec)

    @staticmethod
    def list_orders_by_status(status: str) -> List[Dict]:
        """Return list of orders filtered by status."""
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("status") == status]
