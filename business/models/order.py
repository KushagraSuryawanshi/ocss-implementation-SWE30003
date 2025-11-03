"""
File: order.py
Layer: Business Logic
Component: Domain Model - Order
Description:
    Immutable snapshot of a confirmed purchase.
    Persists items, totals, timestamps, and status.
"""
from typing import Dict, List
from datetime import datetime
from storage.storage_manager import StorageManager

class Order:
    def __init__(self, id: int, customer_id: int, items: List[Dict], total: float, status: str, created_at: str):
        # init order details
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.total = float(total)
        self.status = status  # CREATED, PAID, SHIPPED
        self.created_at = created_at

    # create invoice for this order
    def generate_invoice(self):
        from business.models.invoice import Invoice
        return Invoice.create(self.id, self.total)

    # process payment and mark as paid
    def pay_and_mark(self, payment_method: str = "card"):
        from business.models.payment import PaymentFactory
        payment = PaymentFactory.create(payment_method, self.total, self.id)
        payment.process()
        self.mark_paid()
        return payment

    # create shipment and mark order as shipped
    def ship_with(self, tracking_number: str):
        from business.models.shipment import Shipment
        shipment = Shipment.create(self.id, tracking_number)
        shipment.mark_shipped()
        self.mark_shipped()
        return shipment

    # convert order to dictionary
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at,
        }

    # create and save new order
    @staticmethod
    def create(customer_id: int, items: List[Dict], total: float) -> "Order":
        s = StorageManager()
        rec = s.add("orders", {
            "customer_id": customer_id,
            "items": items,
            "total": float(total),
            "status": "CREATED",
            "created_at": datetime.now().isoformat(),
        })
        return Order.from_dict(rec)

    # find order by id
    @staticmethod
    def find_by_id(order_id: int) -> "Order | None":
        s = StorageManager()
        row = s.find_by_id("orders", order_id)
        return Order.from_dict(row) if row else None

    # create order object from dict
    @staticmethod
    def from_dict(data: Dict) -> "Order":
        return Order(
            id=data["id"],
            customer_id=data["customer_id"],
            items=data.get("items", []),
            total=data["total"],
            status=data["status"],
            created_at=data["created_at"],
        )

    # mark order as paid and update storage
    def mark_paid(self) -> None:
        self.status = "PAID"
        StorageManager().update("orders", self.id, {"status": self.status})

    # mark order as shipped and update storage
    def mark_shipped(self) -> None:
        self.status = "SHIPPED"
        StorageManager().update("orders", self.id, {"status": self.status})

    # get short order summary
    def get_summary(self) -> Dict:
        return {"order_id": self.id, "total": self.total, "status": self.status}
