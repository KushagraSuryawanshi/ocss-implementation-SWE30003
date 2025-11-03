"""
File: cli_controller.py
Layer: Presentation
Description:
        Routes CLI commands to business services with error handling.
"""

from typing import Dict, List
from rich.console import Console
from presentation.formatters import (
    display_products_table, 
    display_cart_table, 
    display_report_table
)
from business.services.auth_service import AuthService
from business.services.cart_service import CartService
from business.services.order_service import OrderService
from business.services.report_service import ReportService
from business.services.staff_service import StaffService
from business.exceptions.errors import (
    InsufficientStockError, 
    CartEmptyError
)

console = Console()

class CLIController:
    def __init__(self):
        # Services are recreated for each command
        self.auth_service = AuthService()
        self.cart_service = CartService()
        self.order_service = OrderService()
        self.report_service = ReportService()
        self.staff_service = StaffService()

    # ---------------------- INITIALIZATION ---------------------- #
    def initialize_system(self) -> Dict:
        """Bootstrap system with sample data."""
        try:
            result = self.auth_service.initialize_system()
            return result
        except Exception as e:
            return {"success": False, "message": f"Initialization failed: {str(e)}"}

    # ---------------------- AUTHENTICATION ---------------------- #
    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and save session to file."""
        return self.auth_service.login(username, password)

    def logout(self) -> Dict:
        """End current session."""
        return self.auth_service.logout()

    # ---------------------- CUSTOMER OPS ------------------------ #
    def browse_products(self, category: str = None) -> List[Dict]:
        """Get product catalogue with stock levels."""
        return self.cart_service.browse_products(category)

    def add_to_cart(self, product_id: int, quantity: int) -> Dict:
        """Add item to current user's cart."""
        # Load session from file on EVERY command
        user = self.auth_service.get_current_user()
        
        if not user:
            return {"success": False, "message": "Please login first"}
        
        if user.get("user_type") != "customer":
            return {"success": False, "message": "Only customers can add to cart"}
        
        return self.cart_service.add_item(
            user["customer_id"], 
            product_id, 
            quantity
        )

    def view_cart(self) -> Dict:
        """Get current user's cart contents."""
        user = self.auth_service.get_current_user()
        
        if not user:
            return {"items": [], "total": 0.0}
        
        return self.cart_service.get_cart(user["customer_id"])

    def checkout(self) -> Dict:
        """Process checkout: create order, invoice, and payment."""
        user = self.auth_service.get_current_user()
        
        if not user:
            return {"success": False, "message": "Please login first"}
        
        try:
            return self.order_service.create_order(user["customer_id"])
        except CartEmptyError as e:
            return {"success": False, "message": str(e)}
        except InsufficientStockError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Checkout failed: {str(e)}"}

    # ---------------------- STAFF OPS --------------------------- #
    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        """Mark order as shipped (staff only)."""
        user = self.auth_service.get_current_user()
        
        if not user or user.get("user_type") != "staff":
            return {"success": False, "message": "Staff access required"}
        
        return self.staff_service.ship_order(order_id, tracking_number)

    def generate_report(self, period: str) -> List[Dict]:
        """Generate sales report for given period."""
        return self.report_service.generate(period)

    def view_pending_orders(self) -> List[Dict]:
        """View orders awaiting shipment."""
        user = self.auth_service.get_current_user()
        if not user or user.get("user_type") != "staff":
            return [{"error": "Staff access required"}]
        return self.staff_service.view_pending_orders()

    def update_stock(self, product_id: int, new_quantity: int) -> Dict:
        """Update inventory level (staff only)."""
        user = self.auth_service.get_current_user()
        
        if not user or user.get("user_type") != "staff":
            return {"success": False, "message": "Staff access required"}
        
        return self.staff_service.update_stock(product_id, new_quantity)

    # ---------------------- DISPLAY HELPERS --------------------- #
    def display_products(self, products: List[Dict]):
        """Format and print product table."""
        display_products_table(products)

    def display_cart(self, cart_data: Dict):
        """Format and print cart table."""
        display_cart_table(cart_data)

    def display_report(self, report_data: List[Dict]):
        """Format and print report table."""
        display_report_table(report_data)