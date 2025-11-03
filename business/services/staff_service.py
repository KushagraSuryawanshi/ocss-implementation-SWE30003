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
        # init storage and inventory
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    # list all unshipped orders
    def view_pending_orders(self) -> List[Dict]:
        return [o for o in self.storage.load("orders") if o["status"] != "SHIPPED"]

    # set product stock directly
    def update_stock(self, product_id: int, new_qty: int) -> Dict:
        """
        Updates stock for a given product without direct printing
        (prevents duplicate console output).
        """
        try:
            self.inventory.set_stock(product_id, new_qty)
            # Return only — no console printing here
            return {"success": True, "message": f"Stock for product {product_id} set to {new_qty}"}
        except Exception as e:
            return {"success": False, "message": f"Error updating stock: {str(e)}"}

    # mark order as shipped and record shipment
    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        order = self.storage.find_by_id("orders", order_id)
        if not order:
            return {"success": False, "message": f"Order {order_id} not found"}
        if order.get("status") != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        shipment = {"order_id": order_id, "tracking_number": tracking_number, "status": "SHIPPED"}
        self.storage.add("shipments", shipment)
        self.storage.update("orders", order_id, {"status": "SHIPPED"})

        return {"success": True, "message": f"Order {order_id} shipped with tracking {tracking_number}"}
