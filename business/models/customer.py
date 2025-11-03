"""
File: customer.py
Layer: Business Logic
Component: Domain Model - Customer
Description:
    Represents a store customer. Links to Account and owns a Cart (via carts.json).
    Provides convenience methods to fetch order history.
"""
from typing import List, Dict, Optional
from storage.storage_manager import StorageManager

class Customer:
    def __init__(self, id: int, name: str, email: str, address: str):
        self.id = id
        self.name = name
        self.email = email
        self.address = address

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Customer":
        return Customer(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            address=data["address"],
        )

    @staticmethod
    def add(name: str, email: str, address: str) -> "Customer":
        s = StorageManager()
        rec = s.add("customers", {"name": name, "email": email, "address": address})
        return Customer.from_dict(rec)

    @staticmethod
    def find_by_id(customer_id: int) -> Optional["Customer"]:
        s = StorageManager()
        row = s.find_by_id("customers", customer_id)
        return Customer.from_dict(row) if row else None

    def order_history(self) -> List[Dict]:
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("customer_id") == self.id]
