"""
File: product.py
Layer: Business Logic
Component: Domain Model - Product
Description:
    Represents a sellable product with descriptive attributes.
    Provides convenience methods for loading and finding products.
"""
from typing import Dict, List, Optional
from storage.storage_manager import StorageManager
from business.models.inventory import Inventory


class Product:
    def __init__(self, id: int, name: str, description: str, price: float, category: str):
        self.id = id
        self.name = name
        self.description = description
        self.price = float(price)
        self.category = category

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
        }

    @staticmethod
    def from_dict(data: dict) -> "Product":
        return Product(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description", "No description available"),
            price=data.get("price", 0.0),
            category=data.get("category", "Uncategorized"),
        )


    @staticmethod
    def get_all() -> List["Product"]:
        s = StorageManager()
        return [Product.from_dict(p) for p in s.load("products")]

    @staticmethod
    def find_by_id(product_id: int) -> Optional["Product"]:
        s = StorageManager()
        row = s.find_by_id("products", product_id)
        return Product.from_dict(row) if row else None

    @staticmethod
    def add(name: str, description: str, price: float, category: str) -> "Product":
        s = StorageManager()
        rec = s.add("products", {
            "name": name, "description": description,
            "price": float(price), "category": category
        })
        return Product.from_dict(rec)
    
    def is_available(self) -> bool:
        """Check if this product has stock available."""
        inv = Inventory.get_instance()
        return inv.check_stock(self.id) > 0
