"""
File: formatters.py
Layer: Presentation
Description:
    Handles terminal output formatting for product listings, carts, and reports.
"""
from rich.table import Table
from rich.console import Console

console = Console()

def display_products_table(products):
    """Show product catalogue in table format."""
    if not products:
        console.print("[yellow]No products found[/yellow]")
        return
    
    table = Table(title="🛒 Product Catalogue")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="blue")
    table.add_column("Price", style="green")
    table.add_column("Stock", style="yellow")

    for p in products:
        stock_display = str(p["stock"]) if p["stock"] > 0 else "[red]Out of Stock[/red]"
        table.add_row(
            str(p["id"]), 
            p["name"],
            p["category"],
            f"${p['price']:.2f}", 
            stock_display
        )
    
    console.print(table)

def display_cart_table(cart):
    """Display shopping cart contents."""
    items = cart.get("items", [])
    
    if not items:
        console.print("[yellow]🛒 Cart is empty[/yellow]")
        return
    
    table = Table(title="🛒 Your Shopping Cart")
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

def display_report_table(report):
    """Display sales or inventory reports."""
    if not report:
        console.print("[yellow]No report data available[/yellow]")
        return
    
    table = Table(title="📊 Report Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="green")

    for r in report:
        table.add_row(r["metric"], str(r["value"]))
    
    console.print(table)