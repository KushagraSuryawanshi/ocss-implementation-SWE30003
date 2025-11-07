"""
Main entry point for the Online Convenience Store System (OCSS).

Runs the CLI application using Typer and delegates all commands
to the presentation layer controller.
"""

import typer
from rich.console import Console
from presentation.cli_controller import CLIController
from storage.session_manager import SessionManager
from storage.storage_manager import StorageManager

app = typer.Typer(
    name="ocss",
    help="Online Convenience Store System (OCSS) - Command-line shop interface",
    add_completion=False,
)

console = Console()
controller = CLIController()

# ---------------------------------------------------------------------
# System setup
# ---------------------------------------------------------------------
@app.command()
def init():
    """Initialize the system with sample data."""
    result = controller.initialize_system()
    if result["success"]:
        console.print("[green]System initialized with sample data.[/green]")
    else:
        console.print(f"[red]{result['message']}[/red]")


# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------
@app.command()
def login(username: str, password: str):
    """Log in as a customer or staff member."""
    result = controller.login(username, password)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result.get('message', 'Login failed')}[/{color}]")


@app.command()
def logout():
    """Log out from the current session."""
    result = controller.logout()
    console.print(f"[green]{result['message']}[/green]")


@app.command()
def whoami():
    """Show the currently logged-in user."""
    session = SessionManager.load_session()
    if session:
        console.print(f"[cyan]Logged in as: {session['username']} ({session['user_type']})[/cyan]")
    else:
        console.print("[yellow]Not logged in.[/yellow]")


# ---------------------------------------------------------------------
# Customer commands
# ---------------------------------------------------------------------
@app.command()
def browse(category: str = typer.Argument(None, help="Optional category filter (e.g. Dairy)")):
    """Browse available products."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return

    products = controller.browse_products(category)
    if not products:
        console.print("[yellow]No products found.[/yellow]")
    else:
        controller.display_products(products)


@app.command(name="add-to-cart")
def add_to_cart(
    product_id: int = typer.Argument(..., help="Product ID"),
    quantity: int = typer.Argument(1, help="Quantity to add (default 1)"),
):

    """Add a product to your shopping cart."""
    result = controller.add_to_cart(product_id, quantity)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result['message']}[/{color}]")


@app.command(name="view-cart")
def view_cart():
    """Display the current shopping cart."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return
    if session.get("user_type") != "customer":
        console.print("[red]Customer access required.[/red]")
        return

    cart = controller.view_cart()
    if not cart.get("items"):
        console.print("[yellow]Your cart is empty.[/yellow]")
    else:
        controller.display_cart(cart)


@app.command()
def checkout():
    """Checkout and process payment for the current cart."""
    result = controller.checkout()
    if not result["success"] and result.get("message") != "Cart is empty":
        console.print(f"[red]{result['message']}[/red]")


@app.command(name="view-invoice")
def view_invoice(order_id: int = typer.Argument(..., help="Order ID to view invoice for")):
    """View the invoice for a completed order."""
    controller.view_invoice(order_id)


# ---------------------------------------------------------------------
# Staff commands
# ---------------------------------------------------------------------
@app.command(name="view-orders")
def view_orders():
    """List all unshipped orders (staff only)."""
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
    else:
        controller.display_orders(orders)


@app.command(name="ship-order")
def ship_order(order_id: int, tracking_number: str):
    """Mark an order as shipped."""
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
def generate_report(period: str = typer.Argument("daily", help="daily | monthly | all")):
    """Generate a sales or inventory report (staff only)."""
    report = controller.generate_report(period)
    if report:
        controller.display_report(report)


@app.command(name="update-stock")
def update_stock(product_id: int, new_quantity: int):
    """Update product stock levels (staff only)."""
    result = controller.update_stock(product_id, new_quantity)
    color = "green" if result["success"] else "red"
    console.print(f"[{color}]{result['message']}[/{color}]")


@app.command(name="order-status")
def order_status(order_id: int):
    """Check the status of a specific order."""
    session = SessionManager.load_session()
    if not session:
        console.print("[red]Please login first.[/red]")
        return

    order = StorageManager().find_by_id("orders", order_id)
    if not order:
        console.print(f"[red]Order {order_id} not found.[/red]")
        return

    status = order.get("status", "UNKNOWN").upper()
    display_status = "NOT SHIPPED" if status == "PAID" else status
    console.print(f"[cyan]Order ID:[/cyan] {order['id']}")
    console.print(f"[cyan]Customer ID:[/cyan] {order['customer_id']}")
    console.print(f"[cyan]Total:[/cyan] ${order['total']:.2f}")
    console.print(f"[cyan]Status:[/cyan] {display_status}")


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app()
