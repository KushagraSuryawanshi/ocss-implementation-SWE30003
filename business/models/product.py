"""
Represents a product available in the online store.
Handles pricing, category, and interaction with the inventory system.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from storage.storage_manager import StorageManager
from business.models.inventory import Inventory


class Product:
    """Represents a sellable item in the store."""

    def __init__(self, id: int, name: str, description: str, price, category: str):
        self.id = id
        self.name = name
        self.description = description
        self.price = Decimal(str(price))
        self.category = category

    # -----------Stock operations--------------------------------------- #

    def reserve_stock(self, qty: int) -> None:
        """Reserves stock for this product."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        inv = Inventory.get_instance()
        inv.reserve_stock(self.id, int(qty))

    def release_stock(self, qty: int) -> None:
        """Releases previously reserved stock."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        inv = Inventory.get_instance()
        inv.release_stock(self.id, int(qty))

    def is_available(self) -> bool:
        """Returns True if this product has available stock."""
        inv = Inventory.get_instance()
        return inv.check_stock(self.id) > 0

    # ------------Persistence------------------------------------------- #

    def to_dict(self) -> Dict:
        """Converts the product to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "category": self.category,
        }

    @staticmethod
    def from_dict(data: dict) -> "Product":
        """Builds a Product object from stored data."""
        return Product(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description", "No description available"),
            price=Decimal(str(data.get("price", 0.0))),
            category=data.get("category", "Uncategorized"),
        )

    @staticmethod
    def get_all() -> List["Product"]:
        """Retrieves all products from storage."""
        s = StorageManager()
        return [Product.from_dict(p) for p in s.load("products")]

    @staticmethod
    def find_by_id(product_id: int) -> Optional["Product"]:
        """Finds a product by its ID."""
        s = StorageManager()
        row = s.find_by_id("products", product_id)
        return Product.from_dict(row) if row else None

    @staticmethod
    def add(name: str, description: str, price, category: str) -> "Product":
        """Adds a new product to storage."""
        s = StorageManager()
        rec = s.add("products", {
            "name": name,
            "description": description,
            "price": float(Decimal(str(price))),
            "category": category,
        })
        return Product.from_dict(rec)

    # ------------Utility--------------------------------------------- #

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price=${self.price})"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.id == other.id
