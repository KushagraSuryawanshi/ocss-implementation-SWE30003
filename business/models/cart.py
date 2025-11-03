"""
File: cart.py
Layer: Business Logic
Component: Domain Model - Cart
Description:
    Represents a customer's shopping cart with line items and totals.
    Persists to carts.json. One active cart per customer.
"""
from typing import Dict, List
from storage.storage_manager import StorageManager
from business.models.product import Product
from business.models.inventory import Inventory

class Cart:
    def __init__(self, id: int, customer_id: int, items: List[Dict]):
        # init cart with id, customer and items list
        self.id = id
        self.customer_id = customer_id
        self.items = items

    # check if cart is empty
    def is_empty(self) -> bool:
        return len(self.items) == 0

    # make snapshot for order creation
    def to_order_snapshot(self) -> Dict:
        return {
            "customer_id": self.customer_id,
            "items": [dict(it) for it in self.items],
            "total": self.total(),
        }

    # reserve inventory for all items
    def reserve_all(self) -> None:
        inv = Inventory.get_instance()
        reserved: List[Dict] = []
        try:
            for it in self.items:
                inv.reserve_stock(it["product_id"], int(it["qty"]))
                reserved.append({"product_id": it["product_id"], "qty": int(it["qty"])})
        except Exception:
            # rollback any reserved stock if failed
            for r in reserved:
                try:
                    inv.release_stock(r["product_id"], r["qty"])
                except Exception:
                    pass
            raise

    # release all reserved inventory
    def release_all(self) -> None:
        inv = Inventory.get_instance()
        for it in self.items:
            inv.release_stock(it["product_id"], int(it["qty"]))

    # clear cart and save
    def clear_and_save(self) -> None:
        self.clear()

    # recalc item subtotals
    def _recalculate(self) -> None:
        for it in self.items:
            it["subtotal"] = float(it["price"]) * int(it["qty"])

    # add new item or update quantity
    def add_item(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        p = Product.find_by_id(product_id)
        if not p:
            raise ValueError("Product not found")

        for it in self.items:
            if it["product_id"] == product_id:
                it["qty"] = int(it["qty"]) + int(qty)
                self._recalculate()
                self._save()
                return

        self.items.append({
            "product_id": p.id,
            "name": p.name,
            "price": float(p.price),
            "qty": int(qty),
            "subtotal": float(p.price) * int(qty),
        })
        self._save()

    # update quantity of a specific item
    def update_quantity(self, product_id: int, qty: int) -> None:
        if qty < 0:
            raise ValueError("Quantity cannot be negative")
        for it in self.items:
            if it["product_id"] == product_id:
                it["qty"] = int(qty)
                if it["qty"] == 0:
                    self.items = [x for x in self.items if x["product_id"] != product_id]
                self._recalculate()
                self._save()
                return
        raise ValueError("Item not in cart")

    # clear all items from cart
    def clear(self) -> None:
        self.items = []
        self._save()

    # calculate total price
    def total(self) -> float:
        return sum(float(it["subtotal"]) for it in self.items)

    # convert cart to dictionary
    def to_dict(self) -> Dict:
        return {"id": self.id, "customer_id": self.customer_id, "items": self.items}

    # save cart to storage
    def _save(self) -> None:
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

    # get existing cart or create a new one
    @staticmethod
    def get_or_create_for_customer(customer_id: int) -> "Cart":
        s = StorageManager()
        carts = s.load("carts")
        for c in carts:
            if c["customer_id"] == customer_id:
                return Cart(id=c["id"], customer_id=c["customer_id"], items=c.get("items", []))
        rec = s.add("carts", {"customer_id": customer_id, "items": []})
        return Cart(id=rec["id"], customer_id=customer_id, items=[])
