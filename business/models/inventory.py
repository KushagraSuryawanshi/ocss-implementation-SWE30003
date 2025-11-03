"""
File: inventory.py
Layer: Business Logic
Component: Domain Model - Inventory (Singleton)
Description:
    Single source of truth for stock. Loads and persists stock levels.
    Provides stock checks, reservation, release, and updates.
"""
from typing import Dict, List
from storage.storage_manager import StorageManager
from business.exceptions.errors import InsufficientStockError

class Inventory:
    _instance = None

    # ensure singleton instance
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # init inventory storage and cache
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._storage = StorageManager()
        self._stock_cache = {}
        self._load_stock()

    # load stock data from storage
    def _load_stock(self) -> None:
        data = self._storage.load("inventory")
        self._stock_cache = {row["product_id"]: int(row["quantity"]) for row in data}

    # save stock data to storage
    def _save_stock(self) -> None:
        data = [{"product_id": pid, "quantity": qty} for pid, qty in self._stock_cache.items()]
        self._storage.save_all("inventory", data)

    # check available stock for product
    def check_stock(self, product_id: int) -> int:
        return int(self._stock_cache.get(product_id, 0))

    # reserve stock for order
    def reserve_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        current = self.check_stock(product_id)
        if current < qty:
            raise InsufficientStockError(f"Only {current} units available for product {product_id}")
        self._stock_cache[product_id] = current - qty
        self._save_stock()

    # release previously reserved stock
    def release_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        current = self.check_stock(product_id)
        self._stock_cache[product_id] = current + qty
        self._save_stock()

    # set stock quantity directly
    def set_stock(self, product_id: int, new_qty: int) -> None:
        if new_qty < 0:
            raise ValueError("Stock cannot be negative")
        self._stock_cache[product_id] = int(new_qty)
        self._save_stock()

    # reserve a list of items in batch
    def reserve_batch(self, items: List[Dict]) -> None:
        reserved = []
        try:
            for it in items:
                pid, qty = int(it["product_id"]), int(it["qty"])
                self.reserve_stock(pid, qty)
                reserved.append({"product_id": pid, "qty": qty})
        except Exception:
            for r in reserved:
                try:
                    self.release_stock(r["product_id"], r["qty"])
                except Exception:
                    pass
            raise

    # release a list of reserved items
    def release_batch(self, items: List[Dict]) -> None:
        for it in items:
            self.release_stock(int(it["product_id"]), int(it["qty"]))

    # get singleton instance
    @classmethod
    def get_instance(cls) -> "Inventory":
        return cls()
