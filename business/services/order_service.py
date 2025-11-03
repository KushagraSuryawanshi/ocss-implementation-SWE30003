"""
File: order_service.py
Layer: Business Logic
Component: Order Service
Description:
    Handles checkout, order creation, invoice, payment, and shipment logic.
    Applies Factory Method for payment and updates Inventory/Cart.
"""
from typing import Dict
from datetime import datetime
from business.models.cart import Cart
from business.models.order import Order
from business.models.invoice import Invoice
from business.models.payment import PaymentFactory
from business.models.inventory import Inventory
from business.models.shipment import Shipment
from storage.storage_manager import StorageManager
from business.exceptions.errors import InsufficientStockError, CartEmptyError

class OrderService:
    def __init__(self):
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    def create_order(self, customer_id: int) -> Dict:
        """Create order from customer's cart with payment and invoice."""
        # Load cart
        cart = Cart.get_or_create_for_customer(customer_id)
        
        if not cart.items:
            raise CartEmptyError("Cannot checkout with empty cart")

        # Calculate total
        total = cart.total()

        # Reserve stock for all items
        try:
            for item in cart.items:
                self.inventory.reserve_stock(item["product_id"], item["qty"])
        except InsufficientStockError as e:
            for item in cart.items:
                self.inventory.release_stock(item["product_id"], item["qty"])
            return {"success": False, "message": str(e)}


        # Create order
        order = Order.create(customer_id, cart.items, total)

        # Create invoice
        invoice = Invoice.create(order.id, total)

        # Process payment (mock)
        payment = PaymentFactory.create("card", total, order.id)
        payment.process()
        
        # Mark invoice as paid
        invoice.mark_paid()
        order.mark_paid()

        # Clear cart
        cart.clear()

        return {
            "success": True, 
            "order_id": order.id, 
            "total": total,
            "invoice_id": invoice.id
        }

    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        """Mark order as shipped and record shipment."""
        order = Order.find_by_id(order_id)
        if not order:
            return {"success": False, "message": "Order not found"}

        if order.status != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        # Create shipment
        shipment = Shipment.create(order_id, tracking_number)
        shipment.mark_shipped()
        
        # Update order status
        order.mark_shipped()
        
        return {
            "success": True, 
            "message": f"Order {order_id} shipped with tracking {tracking_number}"
        }