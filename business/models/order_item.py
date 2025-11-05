"""
Represents a single product entry in an order.
Each OrderItem stores the product, quantity, and the price at the time
the order was placed. This ensures price changes later do not affect
existing orders.
"""

from typing import Dict
from decimal import Decimal


class OrderItem:
    """Immutable record of one product line inside an order."""

    def __init__(self, product, quantity: int, price_snapshot: Decimal = None):
        """Creates a new order item with its product, quantity and price."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Import here to avoid circular dependency
        from business.models.product import Product
        if not isinstance(product, Product):
            raise TypeError("product must be a Product instance")

        self.product = product
        self.quantity = quantity
        self.price_snapshot = (
            Decimal(str(price_snapshot)) if price_snapshot is not None
            else Decimal(str(product.price))
        )
        self.subtotal = self.price_snapshot * quantity

    def to_dict(self) -> Dict:
        """Converts this item into a dictionary for JSON storage."""
        return {
            "product_id": self.product.id,
            "name": self.product.name,
            "quantity": self.quantity,
            "price": float(self.price_snapshot),
            "subtotal": float(self.subtotal),
        }

    @staticmethod
    def from_dict(data: Dict) -> "OrderItem":
        """Rebuilds an OrderItem from stored data."""
        from business.models.product import Product

        product = Product.find_by_id(data["product_id"])
        if not product:
            # Create placeholder product if it was removed from catalogue
            product = Product(
                id=data["product_id"],
                name=data.get("name", f"Product {data['product_id']}"),
                description="Product no longer available",
                price=Decimal(str(data["price"])),
                category="Archived",
            )

        return OrderItem(
            product=product,
            quantity=data.get("quantity", data.get("qty", 0)),
            price_snapshot=Decimal(str(data["price"])),
        )

    def __repr__(self):
        return (
            f"OrderItem(product={self.product.name}, "
            f"qty={self.quantity}, price=${self.price_snapshot})"
        )

    def __eq__(self, other):
        """Two order items are equal if they refer to the same product and price."""
        if not isinstance(other, OrderItem):
            return False
        return (
            self.product.id == other.product.id
            and self.price_snapshot == other.price_snapshot
        )
