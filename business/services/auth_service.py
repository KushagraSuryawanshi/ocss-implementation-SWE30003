"""
File: auth_service.py
Layer: Business Logic
Component: Auth Service
Description:
    Handles user authentication and initial sample data creation.
    Links Account, Customer, and Staff domain objects.
"""
from typing import Optional, Dict
from storage.storage_manager import StorageManager
from storage.session_manager import SessionManager
from business.models.account import Account
from business.models.customer import Customer
from business.models.staff import Staff
from business.models.product import Product
from business.models.inventory import Inventory

class AuthService:
    def __init__(self):
        self.storage = StorageManager()
        self.session_manager = SessionManager()
        # Load existing session
        self.current_user = self.session_manager.load_session()

    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and save session."""
        accounts = self.storage.load("accounts")
        
        for acc in accounts:
            if acc["username"] == username and acc["password"] == password:
                # Save session to file
                self.current_user = acc
                self.session_manager.save_session(acc)
                
                return {
                    "success": True, 
                    "user": acc,
                    "message": f"Logged in as {acc['user_type']}"
                }
        
        return {"success": False, "message": "Invalid credentials"}

    def logout(self) -> Dict:
        """End current session."""
        self.current_user = None
        self.session_manager.clear_session()
        return {"success": True, "message": "Logged out successfully"}

    def get_current_user(self) -> Optional[Dict]:
        """Get current logged-in user (from session file)."""
        if self.current_user is None:
            self.current_user = self.session_manager.load_session()
        return self.current_user

    def initialize_system(self) -> Dict:
        """Create sample customers, staff, products, and inventory."""
        # Clear any existing session on init
        self.session_manager.clear_session()
        
        # Only seed if empty
        if not self.storage.load("products"):
            Product.add("Milk 1L", "Fresh milk bottle", 3.5, "Dairy")
            Product.add("Bread Loaf", "Whole grain loaf", 4.2, "Bakery")
            Product.add("Eggs (12)", "Dozen free-range eggs", 6.8, "Dairy")

        inv = Inventory.get_instance()
        inv.set_stock(1, 50)
        inv.set_stock(2, 25)
        inv.set_stock(3, 30)

        # Customers and staff
        if not self.storage.load("customers"):
            c = Customer.add("John Doe", "john@example.com", "123 Main St, Melbourne")
            Account.add("customer1", "Password123!", "customer", customer_id=c.id)

        if not self.storage.load("staff"):
            s = Staff.add("staff1", "Admin User")
            Account.add("staff1", "Admin123!", "staff", staff_id=s.id)

        return {"success": True, "message": "System initialized with sample data"}