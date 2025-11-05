"""
Represents a single item inside a customer's shopping cart.
Each CartItem stores a Product reference and the selected quantity.
"""

from typing import Dict
from decimal import Decimal


class CartItem:
    """Stores one product and its quantity within a cart."""

    def __init__(self, product, quantity: int):
        """Initializes a cart item with a product and quantity."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Import here to avoid circular imports
        from business.models.product import Product
        if not isinstance(product, Product):
            raise TypeError("Expected a Product instance")

        self.product = product
        self.quantity = quantity
        self._calculate_subtotal()

    def _calculate_subtotal(self) -> None:
        """Calculates subtotal based on product price and quantity."""
        self.subtotal = Decimal(str(self.product.price)) * self.quantity

    def update_quantity(self, new_qty: int) -> None:
        """Updates the item quantity and recalculates subtotal."""
        if new_qty < 0:
            raise ValueError("Quantity cannot be negative")

        self.quantity = new_qty
        self._calculate_subtotal()

    def to_dict(self) -> Dict:
        """Converts the item into a dictionary for JSON storage."""
        return {
            "product_id": self.product.id,
            "name": self.product.name,
            "price": float(self.product.price),
            "qty": self.quantity,
            "subtotal": float(self.subtotal)
        }

    @staticmethod
    def from_dict(data: Dict) -> "CartItem":
        """
        Creates a CartItem from stored data.
        Loads the Product object using its ID.
        """
        from business.models.product import Product

        product = Product.find_by_id(data["product_id"])
        if not product:
            raise ValueError(f"Product {data['product_id']} not found")

        return CartItem(product, data["qty"])

    def __repr__(self):
        return f"CartItem(product={self.product.name}, qty={self.quantity}, subtotal=${self.subtotal})"

    def __eq__(self, other):
        """Returns True if both items refer to the same product."""
        if not isinstance(other, CartItem):
            return False
        return self.product.id == other.product.id
