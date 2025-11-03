"""
File: storage_manager.py
Layer: Data Access
Component: Storage Manager
Description:
    Unified interface for file-based persistence.
    Responsibilities:
      - Map entity types to JSON files
      - Provide CRUD operations
      - Ensure data files exist
      - Maintain ID auto-incrementing
Collaborators:
      - JSONHandler (low-level I/O)
      - app_config (file paths)
"""

from typing import List, Dict, Any, Optional
from app_config import (
    CUSTOMERS_FILE, ACCOUNTS_FILE, PRODUCTS_FILE, INVENTORY_FILE,
    ORDERS_FILE, INVOICES_FILE, PAYMENTS_FILE, SHIPMENTS_FILE,
    CARTS_FILE, STAFF_FILE
)
from storage.json_handler import JSONHandler


class StorageManager:
    """High-level persistence API used by business services."""

    _file_map = {
        "customers": CUSTOMERS_FILE,
        "accounts": ACCOUNTS_FILE,
        "products": PRODUCTS_FILE,
        "inventory": INVENTORY_FILE,
        "orders": ORDERS_FILE,
        "invoices": INVOICES_FILE,
        "payments": PAYMENTS_FILE,
        "shipments": SHIPMENTS_FILE,
        "carts": CARTS_FILE,
        "staff": STAFF_FILE,
    }

    def __init__(self):
        # setup JSON handler and ensure all files exist
        self.json_handler = JSONHandler()
        self.ensure_files()

    # create empty files if missing
    def ensure_files(self) -> None:
        for path in self._file_map.values():
            if not path.exists():
                self.json_handler.write_json(path, [])

    # load all records for entity
    def load(self, entity: str) -> List[Dict[str, Any]]:
        file_path = self._file_map.get(entity)
        if not file_path:
            raise ValueError(f"Unknown entity type: {entity}")
        return self.json_handler.read_json(file_path)

    # alias for backward compatibility
    def get_all(self, entity: str) -> List[Dict[str, Any]]:
        return self.load(entity)

    # keep read() alias for older code
    read = get_all

    # save all records back to file
    def save_all(self, entity: str, data: List[Dict[str, Any]]) -> None:
        file_path = self._file_map.get(entity)
        try:
            self.json_handler.write_json(file_path, data)
        except Exception as e:
            print(f"[ERROR] Failed to save {entity}: {e}")

    # add record with auto-incremented ID
    def add(self, entity: str, record: Dict[str, Any]) -> Dict[str, Any]:
        records = self.load(entity)
        max_id = max((r.get("id", 0) for r in records), default=0)
        record["id"] = max_id + 1
        records.append(record)
        self.save_all(entity, records)
        return record

    # update record by ID
    def update(self, entity: str, record_id: int, updates: Dict[str, Any]) -> bool:
        records = self.load(entity)
        for rec in records:
            if rec.get("id") == record_id:
                rec.update(updates)
                self.save_all(entity, records)
                return True
        return False

    # delete record by ID
    def delete(self, entity: str, record_id: int) -> bool:
        records = self.load(entity)
        new_records = [r for r in records if r.get("id") != record_id]
        if len(new_records) != len(records):
            self.save_all(entity, new_records)
            return True
        return False

    # find single record by ID
    def find_by_id(self, entity: str, record_id: int) -> Optional[Dict[str, Any]]:
        for rec in self.load(entity):
            if rec.get("id") == record_id:
                return rec
        return None
