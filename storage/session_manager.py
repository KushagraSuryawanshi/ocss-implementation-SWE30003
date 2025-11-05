"""
Handles persistent session data for the CLI.
Stores the currently logged-in user between commands.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from app_config import DATA_DIR

SESSION_FILE = DATA_DIR / "session.json"


class SessionManager:
    """Manages user login sessions using a simple JSON file."""

    @staticmethod
    def save_session(user_data: Dict) -> None:
        """Save the current user's session to disk."""
        with open(SESSION_FILE, "w") as f:
            json.dump(user_data, f, indent=2)

    @staticmethod
    def load_session() -> Optional[Dict]:
        """Load session from file if it exists."""
        if not SESSION_FILE.exists():
            return None
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data if data else None
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    @staticmethod
    def clear_session() -> None:
        """Remove session file (logout)."""
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
