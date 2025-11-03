"""
File: session_manager.py
Layer: Storage
Component: Session Manager
Description:
    Manages user session state across CLI commands using file-based storage.
    Each command reads the current session to maintain login state.
"""
import json
from pathlib import Path
from typing import Optional, Dict
from app_config import DATA_DIR

SESSION_FILE = DATA_DIR / "session.json"

class SessionManager:
    """Handles persistent session state for CLI."""

    # save current user session to file
    @staticmethod
    def save_session(user_data: Dict) -> None:
        with open(SESSION_FILE, 'w') as f:
            json.dump(user_data, f, indent=2)

    # load existing session from file
    @staticmethod
    def load_session() -> Optional[Dict]:
        if not SESSION_FILE.exists():
            return None
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                return data if data else None
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    # remove session file to clear login state
    @staticmethod
    def clear_session() -> None:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
