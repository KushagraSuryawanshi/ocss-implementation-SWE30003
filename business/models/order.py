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
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.total = float(total)
        self.status = status               # CREATED, PAID, SHIPPED
        self.created_at = created_at

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at,
        }

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

    @staticmethod
    def find_by_id(order_id: int) -> "Order | None":
        s = StorageManager()
        row = s.find_by_id("orders", order_id)
        return Order.from_dict(row) if row else None

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

    def mark_paid(self) -> None:
        self.status = "PAID"
        StorageManager().update("orders", self.id, {"status": self.status})

    def mark_shipped(self) -> None:
        self.status = "SHIPPED"
        StorageManager().update("orders", self.id, {"status": self.status})

    def get_summary(self) -> Dict:
        """Return short summary for reporting."""
        return {"order_id": self.id, "total": self.total, "status": self.status}
