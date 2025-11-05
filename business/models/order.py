"""
Represents a confirmed customer order.
Stores customer details, purchased items, total cost, and status.
Links directly with Customer, Invoice, Payment, and Shipment.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from storage.storage_manager import StorageManager

if TYPE_CHECKING:
    from business.models.customer import Customer


class Order:
    """Represents a customer's confirmed purchase."""

    def __init__(self, id: int, customer: "Customer", items: List[Dict], total, status: str, created_at: str):
        """Creates an order linked to a Customer object."""
        from business.models.customer import Customer
        if not isinstance(customer, Customer):
            raise TypeError("customer must be a Customer instance")

        self.id = id
        self.customer = customer
        self.items = items
        self.total = Decimal(str(total))
        self.status = status
        self.created_at = created_at

    # -------------Order workflow actions----------------------- #

    def generate_invoice(self):
        """Creates an invoice for this order."""
        from business.models.invoice import Invoice
        return Invoice.create(self.id, self.total)

    def pay_and_mark(self, payment_method: str = "card"):
        """Processes payment and marks the order as paid."""
        from business.models.payment import PaymentFactory
        payment = PaymentFactory.create(payment_method, self.total, self.id)
        payment.process()
        self.mark_paid()
        return payment

    def ship_with(self, tracking_number: str):
        """Creates a shipment and updates the order to 'SHIPPED'."""
        from business.models.shipment import Shipment
        shipment = Shipment.create(self.id, tracking_number)
        shipment.mark_shipped()
        self.mark_shipped()
        return shipment

    # ---------------Persistence------------------------------------------- #

    def to_dict(self) -> Dict:
        """Converts this order into a dictionary for JSON storage."""
        return {
            "id": self.id,
            "customer_id": self.customer.id,
            "items": self.items,
            "total": float(self.total),
            "status": self.status,
            "created_at": self.created_at,
        }

    @staticmethod
    def create(customer_id: int, items: List[Dict], total) -> "Order":
        """Creates and saves a new order for a given customer."""
        from business.models.customer import Customer

        customer = Customer.find_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        s = StorageManager()
        rec = s.add("orders", {
            "customer_id": customer_id,
            "items": items,
            "total": float(Decimal(str(total))),
            "status": "CREATED",
            "created_at": datetime.now().isoformat(),
        })
        return Order.from_dict(rec)

    @staticmethod
    def find_by_id(order_id: int) -> Optional["Order"]:
        """Retrieves an order and reconstructs it with the linked Customer."""
        s = StorageManager()
        row = s.find_by_id("orders", order_id)
        return Order.from_dict(row) if row else None

    @staticmethod
    def from_dict(data: Dict) -> "Order":
        """Builds an Order object from stored JSON data."""
        from business.models.customer import Customer
        customer = Customer.find_by_id(data["customer_id"])
        if not customer:
            raise ValueError(f"Customer {data['customer_id']} not found for order {data['id']}")

        return Order(
            id=data["id"],
            customer=customer,
            items=data.get("items", []),
            total=Decimal(str(data["total"])),
            status=data["status"],
            created_at=data["created_at"],
        )

    # ----------------State updates--------------------------------------------- #

    def mark_paid(self) -> None:
        """Marks the order as paid and updates storage."""
        self.status = "PAID"
        StorageManager().update("orders", self.id, {"status": self.status})

    def mark_shipped(self) -> None:
        """Marks the order as shipped and updates storage."""
        self.status = "SHIPPED"
        StorageManager().update("orders", self.id, {"status": self.status})

    # ------------------Utility--------------------------------------------- #

    def get_summary(self) -> Dict:
        """Returns a short summary of this order."""
        return {
            "order_id": self.id,
            "customer_name": self.customer.name,
            "total": float(self.total),
            "status": self.status,
        }

    def __repr__(self):
        return f"Order(id={self.id}, customer={self.customer.name}, total=${self.total}, status={self.status})"
