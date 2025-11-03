"""
File: json_handler.py
Layer: Data Access
Component: JSON Handler
Description:
    Provides low-level JSON file operations:
      - Safe read and write
      - Automatic file creation
      - Atomic write with Windows-safe rename fallback
"""
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, List, Dict

class JSONHandler:
    """Handles reading and writing JSON files safely."""

    # read JSON file, return list or empty if missing/invalid
    @staticmethod
    def read_json(file_path: Path) -> List[Dict[str, Any]]:
        if not file_path.exists():
            file_path.write_text("[]")
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    # write JSON data atomically with Windows-safe fallback
    @staticmethod
    def write_json(file_path: Path, data: List[Dict[str, Any]]) -> None:
        tmp_path = file_path.with_suffix(".tmp")

        # write to temp file
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # replace file atomically or retry if locked
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
            # final fallback if file still locked
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            shutil.move(tmp_path, file_path)
