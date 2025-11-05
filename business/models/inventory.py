"""
Manages product stock for the entire system.
Implements a Singleton pattern so there is only one inventory instance shared
throughout the application.
"""

from typing import Dict, List
from storage.storage_manager import StorageManager
from business.exceptions.errors import InsufficientStockError


class Inventory:
    """Central store of all product stock levels (Singleton)."""

    _instance = None

    def __new__(cls):
        """Ensures only one Inventory instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initializes the inventory cache and loads data from storage."""
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._storage = StorageManager()
        self._stock_cache: Dict[int, int] = {}
        self._load_stock()

    def _load_stock(self) -> None:
        """Loads stock data from the storage layer."""
        data = self._storage.load("inventory")
        self._stock_cache = {row["product_id"]: int(row["quantity"]) for row in data}

    def _save_stock(self) -> None:
        """Saves current stock levels back to storage."""
        data = [{"product_id": pid, "quantity": qty} for pid, qty in self._stock_cache.items()]
        self._storage.save_all("inventory", data)

    # --- Core operations ---

    def check_stock(self, product_id: int) -> int:
        """Returns the available stock for a product."""
        return int(self._stock_cache.get(product_id, 0))

    def reserve_stock(self, product_id: int, qty: int) -> None:
        """Reserves stock for an order, raising an error if unavailable."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        current = self.check_stock(product_id)
        if current < qty:
            raise InsufficientStockError(f"Only {current} units available for product {product_id}")

        self._stock_cache[product_id] = current - qty
        self._save_stock()

    def release_stock(self, product_id: int, qty: int) -> None:
        """Releases previously reserved stock."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        current = self.check_stock(product_id)
        self._stock_cache[product_id] = current + qty
        self._save_stock()

    def set_stock(self, product_id: int, new_qty: int) -> None:
        """Sets the stock level for a product directly."""
        if new_qty < 0:
            raise ValueError("Stock cannot be negative")

        self._stock_cache[product_id] = int(new_qty)
        self._save_stock()

    # --- Batch operations ---

    def reserve_batch(self, items: List[Dict]) -> None:
        """Reserves stock for multiple items at once, with rollback on failure."""
        reserved = []
        try:
            for it in items:
                pid, qty = int(it["product_id"]), int(it["qty"])
                self.reserve_stock(pid, qty)
                reserved.append({"product_id": pid, "qty": qty})
        except Exception:
            # Roll back any successful reservations if one fails
            for r in reserved:
                try:
                    self.release_stock(r["product_id"], r["qty"])
                except Exception:
                    pass
            raise

    def release_batch(self, items: List[Dict]) -> None:
        """Releases stock for multiple items at once."""
        for it in items:
            self.release_stock(int(it["product_id"]), int(it["qty"]))

    # --- Singleton access ---

    @classmethod
    def get_instance(cls) -> "Inventory":
        """Returns the shared Inventory instance."""
        return cls()
