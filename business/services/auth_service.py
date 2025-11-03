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
        # init storage and session managers
        self.storage = StorageManager()
        self.session_manager = SessionManager()
        # load existing session if any
        self.current_user = self.session_manager.load_session()

    # authenticate user and start session
    def login(self, username: str, password: str) -> Dict:
        accounts = self.storage.load("accounts")
        for acc in accounts:
            if acc["username"] == username and acc["password"] == password:
                self.current_user = acc
                self.session_manager.save_session(acc)
                return {
                    "success": True,
                    "user": acc,
                    "message": f"Logged in as {acc['user_type']}"
                }
        return {"success": False, "message": "Invalid credentials"}

    # logout and clear session
    def logout(self) -> Dict:
        self.current_user = None
        self.session_manager.clear_session()
        return {"success": True, "message": "Logged out successfully"}

    # get current logged-in user
    def get_current_user(self) -> Optional[Dict]:
        if self.current_user is None:
            self.current_user = self.session_manager.load_session()
        return self.current_user

    # initialize sample data for system
    def initialize_system(self) -> Dict:
        self.session_manager.clear_session()

        # seed sample products if empty
        if not self.storage.load("products"):
            Product.add("Milk 1L", "Fresh milk bottle", 3.5, "Dairy")
            Product.add("Bread Loaf", "Whole grain loaf", 4.2, "Bakery")
            Product.add("Eggs (12)", "Dozen free-range eggs", 6.8, "Dairy")

        # set initial stock levels
        inv = Inventory.get_instance()
        inv.set_stock(1, 50)
        inv.set_stock(2, 25)
        inv.set_stock(3, 30)

        # create sample customer and account
        if not self.storage.load("customers"):
            c = Customer.add("John Doe", "john@example.com", "123 Main St, Melbourne")
            Account.add("customer1", "Password123!", "customer", customer_id=c.id)

        # create sample staff and account
        if not self.storage.load("staff"):
            s = Staff.add("staff1", "Admin User")
            Account.add("staff1", "Admin123!", "staff", staff_id=s.id)

        return {"success": True, "message": "System initialized with sample data"}
