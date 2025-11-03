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
from rich.console import Console
from presentation.cli_controller import CLIController
from storage.session_manager import SessionManager

# Initialize Typer application
app = typer.Typer(
    name="ocss",
    help="Online Convenience Store System (OCSS) - Your Local Shop",
    add_completion=False
)

# Console and controller instances
console = Console()
controller = CLIController()

# ------------------------- SYSTEM SETUP COMMANDS ---------------------------- #

@app.command()
def init():
    """Initialize the system with sample data."""
    result = controller.initialize_system()
    if result["success"]:
        console.print("[green]System initialized with sample data[/green]")
    else:
        console.print(f"[red]{result['message']}[/red]")


# ---------------------------- AUTH COMMANDS --------------------------------- #

@app.command()
def login(username: str, password: str):
    """Login as a customer or staff member."""
    result = controller.login(username, password)
    color = "green" if result["success"] else "red"
    message = result.get("message", "Login failed")
    console.print(f"[{color}]{message}[/{color}]")

@app.command()
def logout():
    """Logout from current session."""
    result = controller.logout()
    console.print("[green]Logged out successfully[/green]")

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
def browse(category: str = typer.Argument(None, help="Filter by product category (e.g., Dairy)")):
    """Browse product catalogue."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return

    products = controller.browse_products(category)
    if not products:
        console.print("[yellow]No products found.[/yellow]")
        return
    controller.display_products(products)


@app.command(name="add-to-cart")
def add_to_cart(
    product_id: int = typer.Argument(..., help="Product ID to add"),
    quantity: int = typer.Argument(1, help="Quantity (default: 1)")
):
    """Add item to cart: add-to-cart PRODUCT_ID QUANTITY"""
    result = controller.add_to_cart(product_id, quantity)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result['message']}[/{color}]")

@app.command(name="view-cart")
def view_cart():
    """View the current user's shopping cart."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return
    if session.get("user_type") != "customer":
        console.print("[red]Customer access required.[/red]")
        return

    cart_data = controller.view_cart()
    if not cart_data.get("items"):
        console.print("[yellow]Your cart is empty.[/yellow]")
        return
    controller.display_cart(cart_data)


@app.command()
def checkout():
    """Checkout and process payment for the current cart."""
    result = controller.checkout()
    if not result["success"] and result.get("message") != "Cart is empty":
        console.print(f"[red]{result['message']}[/red]")


# --------------------------- INVOICE COMMAND -------------------------------- #

@app.command(name="view-invoice")
def view_invoice(
    order_id: int = typer.Argument(..., help="Order ID to view invoice for")
):
    """View detailed invoice for a specific order."""
    controller.view_invoice(order_id)


# ----------------------------- STAFF COMMANDS ------------------------------- #

@app.command(name="view-orders")
def view_orders():
    """View all pending orders (staff only)."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return
    if session.get("user_type") != "staff":
        console.print("[red]Staff access required.[/red]")
        return

    orders = controller.view_pending_orders()
    if not orders:
        console.print("[yellow]No pending orders found.[/yellow]")
        return
    controller.display_orders(orders)


@app.command(name="ship-order")
def ship_order(order_id: int = typer.Argument(..., help="Order ID to ship"),
               tracking_number: str = typer.Argument(..., help="Tracking number")):
    """Mark order as shipped (staff only)."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return
    if session.get("user_type") != "staff":
        console.print("[red]Staff access required.[/red]")
        return

    result = controller.ship_order(order_id, tracking_number)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result['message']}[/{color}]")


@app.command(name="generate-report")
def generate_report(period: str = typer.Argument("daily", help="Report period: daily|monthly|all")):
    """Generate sales/inventory reports (staff only)."""
    result = controller.generate_report(period)
    if result:
        controller.display_report(result)

@app.command(name="order-status")
def order_status(order_id: int = typer.Argument(..., help="Order ID to check status")):
    """Check the current status of a specific order."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return

    from storage.storage_manager import StorageManager
    storage = StorageManager()
    order = storage.find_by_id("orders", order_id)

    if not order:
        console.print(f"[red]Order with ID {order_id} not found.[/red]")
        return

    raw_status = order.get("status", "UNKNOWN").upper()
    if raw_status == "PAID":
        display_status = "NOT SHIPPED"
    elif raw_status == "SHIPPED":
        display_status = "SHIPPED"
    else:
        display_status = raw_status

    console.print(f"[cyan]Order ID:[/cyan] {order['id']}")
    console.print(f"[cyan]Customer ID:[/cyan] {order['customer_id']}")
    console.print(f"[cyan]Total:[/cyan] ${order['total']:.2f}")
    console.print(f"[cyan]Status:[/cyan] {display_status}")

@app.command(name="update-stock")
def update_stock(product_id: int, new_quantity: int):
    """Update product stock (staff only)."""
    result = controller.update_stock(product_id, new_quantity)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result['message']}[/{color}]")



# ----------------------------- ENTRY POINT ---------------------------------- #

if __name__ == "__main__":
    app()
