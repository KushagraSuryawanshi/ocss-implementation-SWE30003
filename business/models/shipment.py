"""
Represents the shipping record for an order.
Tracks dispatch details, tracking number, and shipment status.
"""

from typing import Dict, Optional
from datetime import datetime
from storage.storage_manager import StorageManager


class Shipment:
    """Stores information about an order's shipment."""

    def __init__(self, id: int, order_id: int, tracking_number: str, status: str, shipped_at: Optional[str]):
        self.id = id
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.status = status       # "PENDING" or "SHIPPED"
        self.shipped_at = shipped_at

    # -----------Persistence------------------------------------------------------- #

    def to_dict(self) -> Dict:
        """Converts this shipment to a dictionary for storage."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
            "status": self.status,
            "shipped_at": self.shipped_at,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Shipment":
        """Recreates a Shipment object from stored data."""
        return Shipment(
            id=data["id"],
            order_id=data["order_id"],
            tracking_number=data["tracking_number"],
            status=data["status"],
            shipped_at=data.get("shipped_at"),
        )

    @staticmethod
    def create(order_id: int, tracking_number: str) -> "Shipment":
        """Creates and saves a new shipment record for an order."""
        s = StorageManager()
        record = s.add("shipments", {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "status": "PENDING",
            "shipped_at": None,
        })
        return Shipment.from_dict(record)

    @staticmethod
    def find_by_order(order_id: int) -> Optional["Shipment"]:
        """Finds a shipment record by the associated order ID."""
        s = StorageManager()
        for row in s.load("shipments"):
            if row.get("order_id") == order_id:
                return Shipment.from_dict(row)
        return None

    # -----------Business logic--------------------------------------- #

    def mark_shipped(self) -> None:
        """Marks this shipment as shipped and stores the timestamp."""
        self.status = "SHIPPED"
        self.shipped_at = datetime.now().isoformat()  # ISO for consistent date storage

        s = StorageManager()
        s.update("shipments", self.id, {
            "status": self.status,
            "shipped_at": self.shipped_at
        })

    def __repr__(self):
        date_str = self.shipped_at or "Not shipped yet"
        return f"Shipment(id={self.id}, order={self.order_id}, status={self.status}, date={date_str})"
