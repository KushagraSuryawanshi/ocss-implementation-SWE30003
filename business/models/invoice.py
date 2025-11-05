"""
Represents an invoice linked to a specific order.
Handles billing details, payment processing, and paid/unpaid status.
"""

from typing import Dict, Optional
from decimal import Decimal
from storage.storage_manager import StorageManager


class Invoice:
    """Billing record for an order."""

    def __init__(self, id: int, order_id: int, total, paid: bool):
        """Initializes an invoice with total amount and payment state."""
        self.id = id
        self.order_id = order_id
        self.total = Decimal(str(total))  # Use Decimal for accuracy
        self.paid = bool(paid)

    def get_order(self) -> Optional["Order"]:
        """Returns the associated Order object if it exists."""
        from business.models.order import Order
        return Order.find_by_id(self.order_id)

    def pay_via(self, method: str = "card"):
        """Processes payment for this invoice using the chosen method."""
        from business.models.payment import PaymentFactory
        from business.models.order import Order

        payment = PaymentFactory.create(method, self.total, self.order_id)
        payment.process()
        self.mark_paid()

        order = Order.find_by_id(self.order_id)
        if order and order.status != "PAID":
            order.mark_paid()

        return payment

    def to_dict(self) -> Dict:
        """Converts this invoice to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "total": float(self.total),  # Convert Decimal for JSON
            "paid": self.paid
        }

    @staticmethod
    def create(order_id: int, total) -> "Invoice":
        """Creates and saves a new invoice for an order."""
        s = StorageManager()
        rec = s.add("invoices", {
            "order_id": order_id,
            "total": float(Decimal(str(total))),
            "paid": False
        })
        return Invoice.from_dict(rec)

    @staticmethod
    def from_dict(data: Dict) -> "Invoice":
        """Creates an Invoice object from stored data."""
        return Invoice(
            id=data["id"],
            order_id=data["order_id"],
            total=Decimal(str(data["total"])),
            paid=data["paid"]
        )

    def mark_paid(self) -> None:
        """Marks this invoice as paid and updates storage."""
        self.paid = True
        StorageManager().update("invoices", self.id, {"paid": True})

    def __repr__(self):
        status = "PAID" if self.paid else "UNPAID"
        return f"Invoice(id={self.id}, order_id={self.order_id}, total=${self.total}, status={status})"
