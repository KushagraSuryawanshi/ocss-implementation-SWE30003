"""
Provides shopping cart and product browsing functionality for customers.
Integrates product data, stock validation, and cart persistence.
"""

from typing import Dict, List
from decimal import Decimal
from storage.storage_manager import StorageManager
from business.models.product import Product
from business.models.inventory import Inventory
from business.models.cart import Cart


class CartService:
    """Handles cart operations such as adding, removing, and viewing items."""

    def __init__(self):
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    def browse_products(self, category: str | None = None) -> List[Dict]:
        """Returns available products and current stock levels."""
        products = Product.get_all()
        items = []

        for product in products:
            stock = self.inventory.check_stock(product.id)

            if category and product.category.lower() != category.lower():
                continue

            items.append({
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "category": product.category,
                "stock": stock,
            })

        return items

    def add_item(self, customer_id: int, product_id: int, qty: int) -> Dict:
        """Adds an item to a customer's cart if stock allows."""
        if qty <= 0:
            return {"success": False, "message": "Quantity must be positive"}

        product = Product.find_by_id(product_id)
        if not product:
            return {"success": False, "message": "Product not found"}

        available = self.inventory.check_stock(product_id)
        if available < qty:
            return {"success": False, "message": f"Only {available} units available"}
        if qty > 50:
            return {"success": False, "message": "Cannot add more than 50 items"}

        cart = Cart.get_or_create_for_customer(customer_id)

        try:
            cart.add_item(product_id, qty)
            return {"success": True, "message": f"Added {qty}x {product.name} to cart"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_cart(self, customer_id: int) -> Dict:
        """Returns a customer's cart and total value."""
        cart = Cart.get_or_create_for_customer(customer_id)

        if not cart.items:
            return {"items": [], "total": 0.0}

        formatted = []
        for item in cart.items:
            formatted.append({
                "product_id": item.product.id,
                "name": item.product.name,
                "price": float(item.product.price),
                "qty": item.quantity,
                "subtotal": float(item.subtotal),
            })

        return {"items": formatted, "total": float(cart.total())}

    def update_item_quantity(self, customer_id: int, product_id: int, new_qty: int) -> Dict:
        """Updates an item’s quantity or removes it if zero."""
        cart = Cart.get_or_create_for_customer(customer_id)
        try:
            cart.update_quantity(product_id, new_qty)
            return {"success": True, "message": "Cart updated"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def remove_item(self, customer_id: int, product_id: int) -> Dict:
        """Removes an item from the cart."""
        return self.update_item_quantity(customer_id, product_id, 0)

    def clear_cart(self, customer_id: int) -> Dict:
        """Empties a customer's cart."""
        cart = Cart.get_or_create_for_customer(customer_id)
        cart.clear()
        return {"success": True, "message": "Cart cleared"}
