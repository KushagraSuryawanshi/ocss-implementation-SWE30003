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
        # init product details
        self.id = id
        self.name = name
        self.description = description
        self.price = float(price)
        self.category = category

    # convert product to dictionary
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
        }

    # create product object from dictionary
    @staticmethod
    def from_dict(data: dict) -> "Product":
        return Product(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description", "No description available"),
            price=data.get("price", 0.0),
            category=data.get("category", "Uncategorized"),
        )

    # reserve stock in inventory
    def reserve_stock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        inv = Inventory.get_instance()
        inv.reserve_stock(self.id, int(qty))

    # release stock in inventory
    def release_stock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        inv = Inventory.get_instance()
        inv.release_stock(self.id, int(qty))

    # get all products from storage
    @staticmethod
    def get_all() -> List["Product"]:
        s = StorageManager()
        return [Product.from_dict(p) for p in s.load("products")]

    # find product by id
    @staticmethod
    def find_by_id(product_id: int) -> Optional["Product"]:
        s = StorageManager()
        row = s.find_by_id("products", product_id)
        return Product.from_dict(row) if row else None

    # add new product to storage
    @staticmethod
    def add(name: str, description: str, price: float, category: str) -> "Product":
        s = StorageManager()
        rec = s.add("products", {
            "name": name,
            "description": description,
            "price": float(price),
            "category": category
        })
        return Product.from_dict(rec)
    
    # check if product is in stock
    def is_available(self) -> bool:
        inv = Inventory.get_instance()
        return inv.check_stock(self.id) > 0
