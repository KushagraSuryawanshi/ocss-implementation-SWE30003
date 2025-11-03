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
    
    @staticmethod
    def save_session(user_data: Dict) -> None:
        """Save current user session to file."""
        with open(SESSION_FILE, 'w') as f:
            json.dump(user_data, f, indent=2)
    
    @staticmethod
    def load_session() -> Optional[Dict]:
        """Load current user session from file."""
        if not SESSION_FILE.exists():
            return None
        
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                return data if data else None
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    @staticmethod
    def clear_session() -> None:
        """Clear current user session."""
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()