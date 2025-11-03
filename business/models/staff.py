"""
File: staff.py
Layer: Business Logic
Component: Domain Model - Staff
Description:
    Represents staff who manage inventory and shipments.
"""
from typing import Dict, List
from storage.storage_manager import StorageManager

class Staff:
    def __init__(self, id: int, username: str, name: str):
        self.id = id
        self.username = username
        self.name = name

    def to_dict(self) -> Dict:
        return {"id": self.id, "username": self.username, "name": self.name}

    @staticmethod
    def from_dict(data: Dict) -> "Staff":
        return Staff(id=data["id"], username=data["username"], name=data["name"])

    @staticmethod
    def add(username: str, name: str) -> "Staff":
        s = StorageManager()
        rec = s.add("staff", {"username": username, "name": name})
        return Staff.from_dict(rec)

    @staticmethod
    def list_orders_by_status(status: str) -> List[Dict]:
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("status") == status]
