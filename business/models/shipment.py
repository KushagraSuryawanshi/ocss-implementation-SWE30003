"""
File: shipment.py
Layer: Business Logic
Component: Domain Model - Shipment
Description:
    Handles physical dispatch of an Order and tracks shipping status.
"""
from typing import Dict, Optional
from datetime import datetime
from storage.storage_manager import StorageManager

class Shipment:
    def __init__(self, id: int, order_id: int, tracking_number: str, status: str, shipped_at: str | None):
        self.id = id
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.status = status                 # PENDING or SHIPPED
        self.shipped_at = shipped_at

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
            "status": self.status,
            "shipped_at": self.shipped_at
        }

    @staticmethod
    def create(order_id: int, tracking_number: str) -> "Shipment":
        s = StorageManager()
        rec = s.add("shipments", {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "status": "PENDING",
            "shipped_at": None
        })
        return Shipment.from_dict(rec)

    @staticmethod
    def from_dict(data: Dict) -> "Shipment":
        return Shipment(
            id=data["id"],
            order_id=data["order_id"],
            tracking_number=data["tracking_number"],
            status=data["status"],
            shipped_at=data.get("shipped_at"),
        )

    @staticmethod
    def find_by_order(order_id: int) -> Optional["Shipment"]:
        s = StorageManager()
        for sh in s.load("shipments"):
            if sh.get("order_id") == order_id:
                return Shipment.from_dict(sh)
        return None

    def mark_shipped(self) -> None:
        self.status = "SHIPPED"
        self.shipped_at = datetime.now().isoformat()
        StorageManager().update("shipments", self.id, {"status": self.status, "shipped_at": self.shipped_at})
