"""
File: staff_service.py
Layer: Business Logic
Component: Staff Service
Description:
    Provides staff-level operations:
      - Viewing and fulfilling orders
      - Adjusting inventory levels
"""
from typing import Dict, List
from business.models.inventory import Inventory
from storage.storage_manager import StorageManager

class StaffService:
    def __init__(self):
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    def view_pending_orders(self) -> List[Dict]:
        """Return list of all orders not yet shipped."""
        return [o for o in self.storage.load("orders") if o["status"] != "SHIPPED"]

    def update_stock(self, product_id: int, new_qty: int) -> Dict:
        """Directly set stock level for a product."""
        self.inventory.set_stock(product_id, new_qty)
        return {"success": True, "message": f"Stock for product {product_id} set to {new_qty}"}

    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        """Mark order as shipped """
        order = self.storage.find_by_id("orders", order_id)
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        if order.get("status") != "PAID":
            return {"success": False, "message": "Order not yet paid"}
        # Create shipment record
        shipment = {"order_id": order_id, "tracking_number": tracking_number, "status": "SHIPPED"}
        self.storage.add("shipments", shipment)
        self.storage.update("orders", order_id, {"status": "SHIPPED"})
        return {"success": True, "message": f"Order {order_id} shipped with tracking {tracking_number}"}
