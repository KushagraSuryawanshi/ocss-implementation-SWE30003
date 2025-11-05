"""
Utility for safe reading and writing of JSON files.
Handles file creation, atomic saves, and basic error recovery.
"""

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, List, Dict


class JSONHandler:
    """Handles safe JSON file I/O."""

    @staticmethod
    def read_json(file_path: Path) -> List[Dict[str, Any]]:
        """Read a JSON file and return its contents (empty list if missing or invalid)."""
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
        """Write JSON data atomically with a Windows-safe fallback."""
        tmp_path = file_path.with_suffix(".tmp")

        # Write to a temporary file first
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Replace file safely (retry if file is locked)
        try:
            os.replace(tmp_path, file_path)
        except PermissionError:
            for _ in range(3):
                time.sleep(0.1)
                try:
                    os.replace(tmp_path, file_path)
                    return
                except PermissionError:
                    continue
            # Final fallback
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            shutil.move(tmp_path, file_path)
