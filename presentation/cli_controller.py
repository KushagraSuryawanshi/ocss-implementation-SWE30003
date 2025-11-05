"""
Command-line controller that connects user commands to business services.
Handles login, checkout, stock management, and report generation.
"""

from typing import Dict, List
from rich.console import Console
from presentation.formatters import (
    display_products_table,
    display_cart_table,
    display_report_table,
    display_orders_table,
    display_invoice_table,
)
from business.services.auth_service import AuthService
from business.services.cart_service import CartService
from business.services.order_service import OrderService
from business.services.report_service import ReportService
from business.services.staff_service import StaffService
from business.exceptions.errors import InsufficientStockError, CartEmptyError

console = Console()


class CLIController:
    """Top-level command router for the CLI interface."""

    def __init__(self):
        self.auth_service = AuthService()
        self.cart_service = CartService()
        self.order_service = OrderService()
        self.report_service = ReportService()
        self.staff_service = StaffService()

    # ---------- System setup ----------
    def initialize_system(self) -> Dict:
        """Reset storage and load sample data."""
        try:
            return self.auth_service.initialize_system()
        except Exception as e:
            return {"success": False, "message": f"Initialization failed: {e}"}

    # ---------- Auth ----------
    def login(self, username: str, password: str) -> Dict:
        return self.auth_service.login(username, password)

    def logout(self) -> Dict:
        return self.auth_service.logout()

    # ---------- Customer / shared actions ----------
    def browse_products(self, category: str = None) -> List[Dict]:
        """Show product catalogue (optionally filtered by category)."""
        user = self.auth_service.get_current_user()
        if not user:
            console.print("[red]Please login first.[/red]")
            return []

        try:
            products = self.cart_service.browse_products(category)
            if not products:
                console.print("[yellow]No products found.[/yellow]")
            return products
        except Exception as e:
            console.print(f"[red]Failed to load products: {e}[/red]")
            return []

    def add_to_cart(self, product_id: int, quantity: int) -> Dict:
        """Add a product to the current customer’s cart."""
        user = self.auth_service.get_current_user()
        if not user:
            return {"success": False, "message": "Please login first"}
        if user.get("user_type") != "customer":
            return {"success": False, "message": "Customer access required"}
        return self.cart_service.add_item(user["customer_id"], product_id, quantity)

    def view_cart(self) -> Dict:
        """Display the current customer’s cart."""
        user = self.auth_service.get_current_user()
        if not user:
            console.print("[red]Please login first.[/red]")
            return {"items": [], "total": 0.0}
        if user.get("user_type") != "customer":
            console.print("[red]Customer access required.[/red]")
            return {"items": [], "total": 0.0}

        cart = self.cart_service.get_cart(user["customer_id"])
        return cart

    def checkout(self) -> Dict:
        """Process checkout for the logged-in customer."""
        user = self.auth_service.get_current_user()
        if not user or user.get("user_type") != "customer":
            return {"success": False, "message": "Please login first"}

        cart = self.cart_service.get_cart(user["customer_id"])
        if not cart.get("items"):
            console.print("[yellow]Cart is empty.[/yellow]")
            return {"success": False, "message": "Cart is empty"}

        try:
            console.print("\n[bold yellow]Select Payment Method:[/bold yellow]")
            console.print("1. Card\n2. Wallet")
            choice = input("Enter choice (1 or 2): ").strip()
            method = "card" if choice == "1" else "wallet"

            result = self.order_service.create_order(user["customer_id"], payment_method=method)

            if result.get("success"):
                console.print(f"\n[bold green]Payment successful via {method.title()}[/bold green]")
                console.print(f"Invoice ID: {result['invoice_id']} | Order ID: {result['order_id']}")
            else:
                console.print(f"[red]Checkout failed:[/red] {result.get('message')}")
            return result

        except CartEmptyError as e:
            console.print(f"[yellow]{e}[/yellow]")
            return {"success": False, "message": str(e)}
        except InsufficientStockError as e:
            console.print(f"[red]{e}[/red]")
            return {"success": False, "message": str(e)}
        except Exception as e:
            console.print(f"[red]Checkout failed: {e}[/red]")
            return {"success": False, "message": f"Checkout failed: {e}"}

    def view_invoice(self, order_id: int) -> Dict:
        """View invoice for a specific order."""
        user = self.auth_service.get_current_user()
        if not user or user.get("user_type") != "customer":
            console.print("[red]Please login first.[/red]")
            return {}
        result = self.order_service.get_invoice_details(order_id)
        display_invoice_table(result)
        return result

    # ---------- Staff actions ----------
    def ship_order(self, order_id: int, tracking_number: str) -> Dict:
        user = self.auth_service.get_current_user()
        if not user or user.get("user_type") != "staff":
            return {"success": False, "message": "Staff access required"}
        return self.staff_service.ship_order(order_id, tracking_number)

    def generate_report(self, period: str) -> List[Dict]:
        user = self.auth_service.get_current_user()
        if not user:
            console.print("[red]Please login first.[/red]")
            return []
        if user.get("user_type") != "staff":
            console.print("[red]Staff access required.[/red]")
            return []
        return self.report_service.generate(period)

    def view_pending_orders(self) -> List[Dict]:
        user = self.auth_service.get_current_user()
        if not user:
            console.print("[red]Please login first.[/red]")
            return []
        if user.get("user_type") != "staff":
            console.print("[red]Staff access required.[/red]")
            return []
        orders = self.staff_service.view_pending_orders()
        if not orders:
            console.print("[yellow]No pending orders found.[/yellow]")
        return orders

    def update_stock(self, product_id: int, new_quantity: int) -> Dict:
        user = self.auth_service.get_current_user()
        if not user:
            return {"success": False, "message": "Please login first"}
        if user.get("user_type") != "staff":
            return {"success": False, "message": "Staff access required"}
        return self.staff_service.update_stock(product_id, new_quantity)

    # ---------- Display helpers ----------
    def display_products(self, products: List[Dict]):
        display_products_table(products)

    def display_cart(self, cart_data: Dict):
        display_cart_table(cart_data)

    def display_report(self, report_data: List[Dict]):
        display_report_table(report_data)

    def display_orders(self, orders: List[Dict]):
        display_orders_table(orders)
