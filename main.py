"""
===============================================================================
File: main.py
Layer: Presentation (Entry Point)
Description:
    Entry point for the Online Convenience Store System (OCSS).
    Uses Typer to expose user commands for Customers and Staff.
    Routes all commands through CLIController in the Presentation Layer.

    Commands implement the four major scenarios:
    - Browse & Add to Cart (Scenario 1)
    - Checkout & Payment (Scenario 2)
    - Staff Processing Orders (Scenario 3)
    - Reporting (Scenario 4)
===============================================================================
"""

import typer
from typing import Optional
from rich.console import Console
from presentation.cli_controller import CLIController
from storage.session_manager import SessionManager

app = typer.Typer(
    name="ocss",
    help="Online Convenience Store System (OCSS) - Your Local Shop",
    add_completion=False
)

console = Console()
controller = CLIController()

# ------------------------- SYSTEM SETUP COMMANDS ---------------------------- #

@app.command()
def init():
    """Initialize the system with sample data."""
    result = controller.initialize_system()
    if result["success"]:
        console.print("[green]✓ System initialized with sample data[/green]")
    else:
        console.print(f"[red]✗ {result['message']}[/red]")


# ---------------------------- AUTH COMMANDS --------------------------------- #

@app.command()
def login(username: str, password: str):
    """Login as a customer or staff member."""
    result = controller.login(username, password)
    color = "green" if result["success"] else "red"
    symbol = "✓" if result["success"] else "✗"
    message = result.get("message", "Login failed")
    console.print(f"[{color}]{symbol} {message}[/{color}]")


@app.command()
def logout():
    """Logout from current session."""
    result = controller.logout()
    console.print("[green]✓ Logged out successfully[/green]")


@app.command()
def whoami():
    """Show current logged-in user."""
    session = SessionManager.load_session()
    if session:
        console.print(f"[cyan]Logged in as: {session['username']} ({session['user_type']})[/cyan]")
    else:
        console.print("[yellow]Not logged in[/yellow]")


# ---------------------------- CUSTOMER COMMANDS ----------------------------- #

@app.command()
def browse(category: str = typer.Argument(None, help="Filter by product category (eg., Dairy)")):
    """Browse product catalogue."""
    products = controller.browse_products(category)
    controller.display_products(products)



@app.command(name="add-to-cart")
def add_to_cart(
    product_id: int = typer.Argument(..., help="Product ID to add"),
    quantity: int = typer.Argument(1, help="Quantity (default: 1)")
):
    """Add item to cart: add-to-cart PRODUCT_ID QUANTITY"""
    result = controller.add_to_cart(product_id, quantity)
    color = "green" if result["success"] else "red"
    symbol = "✓" if result["success"] else "✗"
    console.print(f"[{color}]{symbol} {result['message']}[/{color}]")


@app.command(name="view-cart")
def view_cart():
    """View the current user's shopping cart."""
    cart_data = controller.view_cart()
    controller.display_cart(cart_data)


@app.command()
def checkout():
    """Checkout and create an order with invoice and payment."""
    result = controller.checkout()
    if result["success"]:
        console.print(f"[green]✓ Order {result['order_id']} created successfully[/green]")
        console.print(f"[cyan]Total: ${result['total']:.2f}[/cyan]")
    else:
        console.print(f"[red]✗ {result['message']}[/red]")


# ----------------------------- STAFF COMMANDS ------------------------------- #

@app.command(name="view-orders")
def view_orders():
    """View all pending orders (staff only)."""
    orders = controller.view_pending_orders()
    console.print(orders)

@app.command(name="ship-order")
def ship_order(
    order_id: int = typer.Argument(..., help="Order ID to ship"),
    tracking_number: str = typer.Argument(..., help="Tracking number")
):
    """Mark order as shipped: ship-order ORDER_ID TRACKING_NUMBER"""
    result = controller.ship_order(order_id, tracking_number)
    color = "green" if result["success"] else "red"
    symbol = "✓" if result["success"] else "✗"
    console.print(f"[{color}]{symbol} {result['message']}[/{color}]")


@app.command(name="generate-report")
def generate_report(period: str = typer.Argument("daily", help="Report period: daily|monthly|all")):
    """Generate sales/inventory reports."""
    result = controller.generate_report(period)
    controller.display_report(result)


# ----------------------------- ENTRY POINT ---------------------------------- #

if __name__ == "__main__":
    app()