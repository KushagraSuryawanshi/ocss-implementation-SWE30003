"""
File: invoice.py
Layer: Business Logic
Component: Domain Model - Invoice
Description:
    Billing record for an Order. Tracks payment state and total.
"""
from typing import Dict
from storage.storage_manager import StorageManager

class Invoice:
    def __init__(self, id: int, order_id: int, total: float, paid: bool):
        self.id = id
        self.order_id = order_id
        self.total = float(total)
        self.paid = bool(paid)

    def to_dict(self) -> Dict:
        return {"id": self.id, "order_id": self.order_id, "total": self.total, "paid": self.paid}

    @staticmethod
    def create(order_id: int, total: float) -> "Invoice":
        s = StorageManager()
        rec = s.add("invoices", {"order_id": order_id, "total": float(total), "paid": False})
        return Invoice.from_dict(rec)

    @staticmethod
    def from_dict(data: Dict) -> "Invoice":
        return Invoice(id=data["id"], order_id=data["order_id"], total=data["total"], paid=data["paid"])

    def mark_paid(self) -> None:
        self.paid = True
        StorageManager().update("invoices", self.id, {"paid": True})
