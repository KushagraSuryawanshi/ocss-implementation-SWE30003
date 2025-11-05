"""
Formatting helpers for displaying tables in the terminal.
Used by the CLI to show products, carts, invoices, reports, and orders.
"""

from rich.table import Table
from rich.console import Console

console = Console()

# ---------Product catalogue display----------------------------------------------------------
def display_products_table(products):
    """Show all products in a formatted table."""
    if not products:
        console.print("[yellow]No products found[/yellow]")
        return

    table = Table(title="Product Catalogue")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="blue")
    table.add_column("Price", style="green")
    table.add_column("Stock", style="yellow")

    for p in products:
        stock_text = str(p["stock"]) if p["stock"] > 0 else "[red]Out of Stock[/red]"
        table.add_row(str(p["id"]), p["name"], p["category"], f"${p['price']:.2f}", stock_text)

    console.print(table)


# ---------Shopping cart display----------------------------------------------------------
def display_cart_table(cart):
    """Show items currently in the user's cart."""
    items = cart.get("items", [])
    if not items:
        console.print("[yellow]Cart is empty[/yellow]")
        return

    table = Table(title="Your Shopping Cart")
    table.add_column("Product", style="cyan")
    table.add_column("Qty", justify="right", style="yellow")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Subtotal", justify="right", style="magenta")

    for item in items:
        table.add_row(
            item["name"],
            str(item["qty"]),
            f"${item['price']:.2f}",
            f"${item['subtotal']:.2f}"
        )

    console.print(table)
    console.print(f"\n[bold green]Total: ${cart.get('total', 0.0):.2f}[/bold green]")


# ----------Invoice display-----------------------------------------------------------
def display_invoice_table(invoice):
    """Show invoice summary and item breakdown."""
    if not invoice.get("success"):
        console.print(f"[red]{invoice.get('message', 'Invoice not found')}[/red]")
        return

    console.print("\n[bold cyan]Invoice Summary[/bold cyan]")
    console.print(
        f"[dim]Order ID:[/dim] {invoice['order_id']}   "
        f"[dim]Invoice ID:[/dim] {invoice['invoice_id']}   "
        f"[dim]Method:[/dim] {invoice['payment_method']}"
    )
    console.print(
        f"[dim]Status:[/dim] "
        f"{'[green]Paid[/green]' if invoice['paid'] else '[red]Unpaid[/red]'}   "
        f"[dim]Total:[/dim] [bold cyan]${invoice['total']:.2f}[/bold cyan]\n"
    )

    table = Table(title="Invoice Details")
    table.add_column("Product", style="cyan")
    table.add_column("Qty", justify="right", style="yellow")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Subtotal", justify="right", style="magenta")

    for item in invoice["items"]:
        subtotal = item["quantity"] * item["price"]
        table.add_row(
            item["product"],
            str(item["quantity"]),
            f"${item['price']:.2f}",
            f"${subtotal:.2f}"
        )

    console.print(table)
    console.print()


# -----------Report display---------------------------------------------------------------------
def display_report_table(report):
    """Show a simple summary of report metrics."""
    if not report:
        console.print("[yellow]No report data available[/yellow]")
        return

    table = Table(title="Report Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    for r in report:
        table.add_row(r["metric"], str(r["value"]))

    console.print(table)


# ---------Orders display-----------------------------------------------------
def display_orders_table(orders: list):
    """Show all orders with their items."""
    if not orders:
        console.print("[yellow]No orders found.[/yellow]")
        return

    for order in orders:
        table = Table(
            title=f"Order ID: {order['id']} | "
                  f"Status: {order['status']} | "
                  f"Total: ${order['total']:.2f}"
        )
        table.add_column("Product ID", justify="right")
        table.add_column("Name")
        table.add_column("Qty", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Subtotal", justify="right")

        for item in order.get("items", []):
            table.add_row(
                str(item["product_id"]),
                item["name"],
                str(item["quantity"]),
                f"${item['price']:.2f}",
                f"${item['subtotal']:.2f}"
            )

        console.print(table)
        console.print()  # space between orders
