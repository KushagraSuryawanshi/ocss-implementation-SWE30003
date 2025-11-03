"""
File: json_handler.py
Layer: Data Access
Component: JSON Handler
Description:
    Provides low-level JSON file operations:
      - Safe read and write
      - Automatic file creation
      - Atomic write to prevent data loss
"""
import json
from pathlib import Path
from typing import Any, List, Dict

class JSONHandler:
    """Handles reading and writing JSON files safely."""

    @staticmethod
    def read_json(file_path: Path) -> List[Dict[str, Any]]:
        """Return list of dictionaries from JSON file, empty list if invalid."""
        if not file_path.exists():
            file_path.write_text("[]")
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    @staticmethod
    def write_json(file_path: Path, data: List[Dict[str, Any]]) -> None:
        """Write JSON data to file with indentation."""
        tmp_path = file_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(file_path)
