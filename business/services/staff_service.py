"""
Provides staff operations for managing orders and inventory.
Staff can view pending orders, mark them as shipped, and adjust stock levels.
"""

from typing import Dict, List
from business.models.inventory import Inventory
from storage.storage_manager import StorageManager


class StaffService:
    """Handles staff-side actions like shipping orders and updating stock."""

    def __init__(self):
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    def view_pending_orders(self) -> List[Dict]:
        """Returns all orders that haven't been shipped yet."""
        orders = self.storage.load("orders")
        return [o for o in orders if o.get("status") != "SHIPPED"]

    def update_stock(self, product_id: int, new_qty: int) -> Dict:
        """Directly updates product stock in the inventory."""
        try:
            self.inventory.set_stock(product_id, new_qty)
            return {"success": True, "message": f"Stock for product {product_id} set to {new_qty}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to update stock: {e}"}

    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        """Marks an order as shipped and records shipment information."""
        order = self.storage.find_by_id("orders", order_id)
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        if order.get("status") != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        # Record shipment and update order status
        shipment = {"order_id": order_id, "tracking_number": tracking_number, "status": "SHIPPED"}
        self.storage.add("shipments", shipment)
        self.storage.update("orders", order_id, {"status": "SHIPPED"})

        return {"success": True, "message": f"Order {order_id} shipped with tracking {tracking_number}"}
