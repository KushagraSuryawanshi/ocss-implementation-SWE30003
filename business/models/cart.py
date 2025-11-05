"""
Defines the Cart class which manages a customer's shopping cart.
Each cart stores CartItem objects that reference real Product instances.
"""

from typing import Dict, List
from decimal import Decimal
from storage.storage_manager import StorageManager
from business.models.product import Product
from business.models.cart_item import CartItem
from business.models.inventory import Inventory


class Cart:
    def __init__(self, id: int, customer_id: int, items: List[CartItem] = None):
        """Initializes a new cart for a given customer."""
        self.id = id
        self.customer_id = customer_id
        self.items: List[CartItem] = items if items else []

    def is_empty(self) -> bool:
        """Returns True if the cart has no items."""
        return len(self.items) == 0

    def to_order_snapshot(self) -> Dict:
        """Converts cart contents into a snapshot dictionary for order creation."""
        return {
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items],
            "total": float(self.total())
        }

    def reserve_all(self) -> None:
        """Reserves stock for all items in the cart."""
        inv = Inventory.get_instance()
        reserved: List[Dict] = []
        try:
            for cart_item in self.items:
                inv.reserve_stock(cart_item.product.id, cart_item.quantity)
                reserved.append({
                    "product_id": cart_item.product.id,
                    "qty": cart_item.quantity
                })
        except Exception:
            # Roll back any reservations if one fails
            for r in reserved:
                try:
                    inv.release_stock(r["product_id"], r["qty"])
                except Exception:
                    pass
            raise

    def release_all(self) -> None:
        """Releases any reserved stock for this cart."""
        inv = Inventory.get_instance()
        for cart_item in self.items:
            inv.release_stock(cart_item.product.id, cart_item.quantity)

    def clear_and_save(self) -> None:
        """Clears the cart and updates storage."""
        self.clear()

    def add_item(self, product_id: int, qty: int) -> None:
        """Adds a product to the cart or updates quantity if it already exists."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        p = Product.find_by_id(product_id)
        if not p:
            raise ValueError("Product not found")

        for cart_item in self.items:
            if cart_item.product.id == product_id:
                cart_item.update_quantity(cart_item.quantity + qty)
                self._save()
                return

        new_item = CartItem(p, qty)
        self.items.append(new_item)
        self._save()

    def update_quantity(self, product_id: int, qty: int) -> None:
        """Updates the quantity of a product in the cart (0 removes it)."""
        if qty < 0:
            raise ValueError("Quantity cannot be negative")

        for cart_item in self.items:
            if cart_item.product.id == product_id:
                if qty == 0:
                    self.items.remove(cart_item)
                else:
                    cart_item.update_quantity(qty)
                self._save()
                return

        raise ValueError("Item not found in cart")

    def clear(self) -> None:
        """Removes all items from the cart."""
        self.items = []
        self._save()

    def total(self) -> Decimal:
        """Calculates the total value of the cart as a Decimal."""
        return sum((item.subtotal for item in self.items), Decimal("0"))

    # ---------------- Persistence ----------------

    def to_dict(self) -> Dict:
        """Converts the cart into a dictionary for JSON storage."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items]
        }

    @staticmethod
    def from_dict(data: Dict) -> "Cart":
        """Recreates a Cart object from stored data."""
        items = []
        for item_dict in data.get("items", []):
            try:
                cart_item = CartItem.from_dict(item_dict)
                items.append(cart_item)
            except ValueError:
                # Skip deleted products
                pass

        return Cart(
            id=data["id"],
            customer_id=data["customer_id"],
            items=items
        )

    def _save(self) -> None:
        """Updates this cart record in persistent storage."""
        s = StorageManager()
        carts = s.load("carts")
        found = False
        for c in carts:
            if c["id"] == self.id:
                c.update(self.to_dict())
                found = True
                break
        if not found:
            carts.append(self.to_dict())
        s.save_all("carts", carts)

    @staticmethod
    def get_or_create_for_customer(customer_id: int) -> "Cart":
        """Finds an existing cart for a customer, or creates a new one."""
        s = StorageManager()
        carts = s.load("carts")
        for c in carts:
            if c["customer_id"] == customer_id:
                return Cart.from_dict(c)

        rec = s.add("carts", {"customer_id": customer_id, "items": []})
        return Cart.from_dict(rec)

    def __repr__(self):
        return f"Cart(id={self.id}, items={len(self.items)}, total=${self.total()})"
