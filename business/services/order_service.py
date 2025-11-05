"""
Manages the full checkout and order lifecycle.
Covers order creation, payment, invoice generation, and shipment.
"""

from typing import Dict
from decimal import Decimal
from business.models.cart import Cart
from business.models.order import Order
from business.models.invoice import Invoice
from business.models.payment import PaymentFactory
from business.models.inventory import Inventory
from business.models.shipment import Shipment
from business.exceptions.errors import InsufficientStockError, CartEmptyError
from storage.storage_manager import StorageManager


class OrderService:
    """Handles checkout logic and ensures orders are processed correctly."""

    def __init__(self):
        self.inventory = Inventory.get_instance()

    def create_order(self, customer_id: int, payment_method: str = "card") -> Dict:
        """Creates an order, processes payment, and generates invoice."""
        cart = Cart.get_or_create_for_customer(customer_id)
        if not cart.items:
            raise CartEmptyError("Cannot checkout with empty cart")

        total = cart.total()

        try:
            cart.reserve_all()
        except InsufficientStockError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            cart.release_all()
            return {"success": False, "message": f"Stock reservation failed: {e}"}

        order_items = [
            {
                "product_id": i.product.id,
                "name": i.product.name,
                "quantity": i.quantity,
                "price": float(i.product.price),
                "subtotal": float(i.subtotal),
            }
            for i in cart.items
        ]

        try:
            order = Order.create(customer_id, order_items, total)
        except ValueError as e:
            cart.release_all()
            return {"success": False, "message": str(e)}

        invoice = Invoice.create(order.id, total)

        try:
            payment = PaymentFactory.create(payment_method, total, order.id)
            msg = payment.process()
        except Exception as e:
            cart.release_all()
            return {"success": False, "message": f"Payment failed: {e}"}

        invoice.mark_paid()
        order.mark_paid()
        cart.clear()

        return {
            "success": True,
            "order_id": order.id,
            "invoice_id": invoice.id,
            "payment_method": payment_method,
            "total": float(total),
            "message": msg,
        }

    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        """Marks an order as shipped and records shipment info."""
        order = Order.find_by_id(order_id)
        if not order:
            return {"success": False, "message": "Order not found"}
        if order.status != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        shipment = Shipment.create(order_id, tracking_number)
        shipment.mark_shipped()
        order.mark_shipped()

        return {"success": True, "message": f"Order {order_id} shipped with tracking {tracking_number}"}

    def get_invoice_details(self, order_id: int) -> Dict:
        """Returns the invoice and payment details for a given order."""
        storage = StorageManager()
        order_data = storage.find_by_id("orders", order_id)
        if not order_data:
            return {"success": False, "message": f"Order {order_id} not found"}

        invoices = storage.load("invoices")
        payments = storage.load("payments")

        invoice = next((i for i in invoices if i["order_id"] == order_id), None)
        if not invoice:
            return {"success": False, "message": f"No invoice found for order {order_id}"}

        payment = next((p for p in payments if p["order_id"] == order_id), None)
        method = payment["method"].title() if payment else "Unknown"

        items = []
        for item in order_data.get("items", []):
            name = item.get("name", f"Product {item.get('product_id', '?')}")
            qty = item.get("quantity", item.get("qty", 0))
            price = float(item.get("price", 0))
            subtotal = float(item.get("subtotal", qty * price))
            items.append({
                "product": name,
                "quantity": qty,
                "price": price,
                "subtotal": subtotal,
            })

        return {
            "success": True,
            "order_id": order_data["id"],
            "invoice_id": invoice["id"],
            "payment_method": method,
            "total": invoice["total"],
            "paid": invoice["paid"],
            "items": items,
        }
