"""
Handles authentication, session management, and system initialization.
Links customer and staff accounts to their respective user records.
"""

from typing import Optional, Dict
from decimal import Decimal
from storage.storage_manager import StorageManager
from storage.session_manager import SessionManager
from business.models.account import Account
from business.models.customer import Customer
from business.models.staff import Staff
from business.models.product import Product
from business.models.inventory import Inventory


class AuthService:
    """Manages user login, logout, and system bootstrapping."""

    def __init__(self):
        self.storage = StorageManager()
        self.session_manager = SessionManager()
        self.current_user = self.session_manager.load_session()

    def login(self, username: str, password: str) -> Dict:
        """Authenticates a user and stores session info."""
        account = self._load_account_with_relationships(username)

        if not account or not account.verify(password):
            return {"success": False, "message": "Invalid credentials"}

        session_data = account.to_dict()
        self.current_user = session_data
        self.session_manager.save_session(session_data)

        return {
            "success": True,
            "user": session_data,
            "message": f"Logged in as {account.user_type}",
        }

    def _load_account_with_relationships(self, username: str) -> Optional[Account]:
        """Loads an account and reconnects linked customer/staff objects."""
        accounts = self.storage.load("accounts")

        for acc_data in accounts:
            if acc_data["username"] == username:
                account = Account.from_dict(acc_data)

                # Restore linked relationships
                if account.user_type == "customer" and acc_data.get("customer_id"):
                    customer = Customer.find_by_id(acc_data["customer_id"])
                    if customer:
                        account.set_customer(customer)

                elif account.user_type == "staff" and acc_data.get("staff_id"):
                    staff = Staff.find_by_id(acc_data["staff_id"])
                    if staff:
                        account.set_staff(staff)

                return account
        return None

    def logout(self) -> Dict:
        """Clears the active session."""
        self.current_user = None
        self.session_manager.clear_session()
        return {"success": True, "message": "Logged out successfully"}

    def get_current_user(self) -> Optional[Dict]:
        """Returns current user from session, if any."""
        if self.current_user is None:
            self.current_user = self.session_manager.load_session()
        return self.current_user

    def initialize_system(self) -> Dict:
        """
        Populates default users, accounts, and sample products.
        Also resets stock levels to a known state.
        """
        self.session_manager.clear_session()

        # Sample products
        if not self.storage.load("products"):
            Product.add("Milk 1L", "Fresh milk bottle", Decimal("3.5"), "Dairy")
            Product.add("Bread Loaf", "Whole grain loaf", Decimal("4.2"), "Bakery")
            Product.add("Eggs (12)", "Dozen free-range eggs", Decimal("6.8"), "Dairy")

        # Inventory defaults
        inv = Inventory.get_instance()
        inv.set_stock(1, 50)
        inv.set_stock(2, 25)
        inv.set_stock(3, 30)

        # Create customer with linked account
        if not self.storage.load("customers"):
            customer = Customer.add("John Doe", "john@example.com", "123 Main St, Melbourne")
            account = Account.add("customer1", "Password123!", "customer")
            customer.set_account(account)
            self.storage.update("accounts", account.id, {"customer_id": customer.id})

        # Create staff with linked account
        if not self.storage.load("staff"):
            staff = Staff.add("staff1", "Admin User")
            account = Account.add("staff1", "Admin123!", "staff")
            staff.set_account(account)
            self.storage.update("accounts", account.id, {"staff_id": staff.id})

        return {"success": True, "message": "System initialized with sample data"}
