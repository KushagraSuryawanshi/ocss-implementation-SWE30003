"""
File: order_service.py
Layer: Business Logic
Component: Order Service
Description:
    Handles checkout, order creation, invoice, payment, and shipment logic.
    Applies Factory Method for payment and updates Inventory/Cart.
"""
from typing import Dict
from business.models.cart import Cart
from business.models.order import Order
from business.models.invoice import Invoice
from business.models.payment import PaymentFactory
from business.models.inventory import Inventory
from business.models.shipment import Shipment
from business.exceptions.errors import InsufficientStockError, CartEmptyError
from storage.storage_manager import StorageManager


class OrderService:
    def __init__(self):
        # init inventory singleton
        self.inventory = Inventory.get_instance()

    # create order from cart and process payment
    def create_order(self, customer_id: int, payment_method: str = "card") -> Dict:
        cart = Cart.get_or_create_for_customer(customer_id)
        if not cart.items:
            raise CartEmptyError("Cannot checkout with empty cart")

        total = cart.total()

        # reserve stock before creating order
        try:
            cart.reserve_all()
        except InsufficientStockError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            try:
                cart.release_all()
            except Exception:
                pass
            return {"success": False, "message": f"Stock reservation failed: {str(e)}"}

        # snapshot cart items for order
        order_items = []
        for item in cart.items:
            order_items.append({
                "product_id": item["product_id"],
                "name": item["name"],
                "quantity": item.get("qty", 0),
                "price": float(item.get("price", 0)),
                "subtotal": float(item.get("subtotal", 0)),
            })

        # create order and invoice
        order = Order.create(customer_id, order_items, total)
        invoice = Invoice.create(order.id, total)

        # process payment
        try:
            payment = PaymentFactory.create(payment_method, total, order.id)
            payment_message = payment.process()
        except Exception as e:
            cart.release_all()
            return {"success": False, "message": f"Payment failed: {str(e)}"}

        # mark invoice and order as paid
        invoice.mark_paid()
        order.mark_paid()

        # clear cart after success
        cart.clear()

        return {
            "success": True,
            "order_id": order.id,
            "total": total,
            "invoice_id": invoice.id,
            "payment_method": payment_method,
            "message": payment_message,
        }

    # mark order as shipped and record shipment
    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        order = Order.find_by_id(order_id)
        if not order:
            return {"success": False, "message": "Order not found"}
        if order.status != "PAID":
            return {"success": False, "message": "Order not yet paid"}

        shipment = Shipment.create(order_id, tracking_number)
        shipment.mark_shipped()
        order.mark_shipped()
        return {
            "success": True,
            "message": f"Order {order_id} shipped with tracking {tracking_number}"
        }

    # fetch detailed invoice and payment info
    def get_invoice_details(self, order_id: int) -> Dict:
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
        payment_method = payment["method"].title() if payment else "Unknown"

        # build item list for invoice view
        items = []
        for item in order_data.get("items", []):
            product_name = item.get("name", f"Product {item.get('product_id', '?')}")
            quantity = item.get("quantity", item.get("qty", 0))
            price = float(item.get("price", 0))
            subtotal = float(item.get("subtotal", quantity * price))
            items.append({
                "product": product_name,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal
            })

        return {
            "success": True,
            "order_id": order_data["id"],
            "invoice_id": invoice["id"],
            "payment_method": payment_method,
            "total": invoice["total"],
            "paid": invoice["paid"],
            "items": items,
        }
