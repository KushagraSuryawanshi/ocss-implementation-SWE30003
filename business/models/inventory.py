"""
File: inventory.py
Layer: Business Logic
Component: Domain Model - Inventory (Singleton)
Description:
    Single source of truth for stock. Loads and persists stock levels.
    Provides stock checks, reservation, release, and updates.
"""
from typing import Dict
from storage.storage_manager import StorageManager
from business.exceptions.errors import InsufficientStockError

class Inventory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._storage = StorageManager()
        self._stock_cache = {}
        self._load_stock()

    def _load_stock(self) -> None:
        """Load stock from storage into memory cache."""
        data = self._storage.load("inventory")
        self._stock_cache = {row["product_id"]: int(row["quantity"]) for row in data}

    def _save_stock(self) -> None:
        """Persist cache back to storage."""
        data = [{"product_id": pid, "quantity": qty} for pid, qty in self._stock_cache.items()]
        self._storage.save_all("inventory", data)

    def check_stock(self, product_id: int) -> int:
        """Get current stock level for product."""
        return int(self._stock_cache.get(product_id, 0))

    def reserve_stock(self, product_id: int, qty: int) -> None:
        """Reserve stock for order. Raises InsufficientStockError if unavailable."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        
        current = self.check_stock(product_id)
        if current < qty:
            raise InsufficientStockError(
                f"Only {current} units available for product {product_id}"
            )
        
        self._stock_cache[product_id] = current - qty
        self._save_stock()

    def release_stock(self, product_id: int, qty: int) -> None:
        """Release reserved stock (e.g., order cancelled)."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        
        current = self.check_stock(product_id)
        self._stock_cache[product_id] = current + qty
        self._save_stock()

    def set_stock(self, product_id: int, new_qty: int) -> None:
        """Set stock level directly (staff operation)."""
        if new_qty < 0:
            raise ValueError("Stock cannot be negative")
        
        self._stock_cache[product_id] = int(new_qty)
        self._save_stock()

    @classmethod
    def get_instance(cls) -> "Inventory":
        """Get singleton instance."""
        return cls()