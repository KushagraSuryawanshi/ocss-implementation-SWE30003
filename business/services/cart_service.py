"""
File: cart_service.py
Layer: Business Logic
Component: Cart Service
Description:
    Manages customer's cart lifecycle and product browsing.
    Validates stock via Inventory Singleton.
"""
from typing import Dict, List
from storage.storage_manager import StorageManager
from business.models.product import Product
from business.models.inventory import Inventory
from business.models.cart import Cart

class CartService:
    def __init__(self):
        # init storage and inventory
        self.storage = StorageManager()
        self.inventory = Inventory.get_instance()

    # list products with stock info
    def browse_products(self, category: str | None = None) -> List[Dict]:
        products = Product.get_all()
        results = []
        for p in products:
            stock = self.inventory.check_stock(p.id)
            if category and p.category.lower() != category.lower():
                continue
            results.append({
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "category": p.category,
                "stock": stock
            })
        return results

    # add product to customer cart after validation
    def add_item(self, customer_id: int, product_id: int, qty: int) -> Dict:
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

    # get current customer cart
    def get_cart(self, customer_id: int) -> Dict:
        cart = Cart.get_or_create_for_customer(customer_id)
        if not cart.items:
            return {"items": [], "total": 0.0}

        formatted_items = []
        for item in cart.items:
            formatted_items.append({
                "product_id": item["product_id"],
                "name": item["name"],
                "price": float(item["price"]),
                "qty": int(item["qty"]),
                "subtotal": float(item["subtotal"])
            })
        return {"items": formatted_items, "total": cart.total()}

    # update quantity of product in cart
    def update_item_quantity(self, customer_id: int, product_id: int, new_qty: int) -> Dict:
        cart = Cart.get_or_create_for_customer(customer_id)
        try:
            cart.update_quantity(product_id, new_qty)
            return {"success": True, "message": "Cart updated"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # remove product from cart
    def remove_item(self, customer_id: int, product_id: int) -> Dict:
        return self.update_item_quantity(customer_id, product_id, 0)

    # clear all items from cart
    def clear_cart(self, customer_id: int) -> Dict:
        cart = Cart.get_or_create_for_customer(customer_id)
        cart.clear()
        return {"success": True, "message": "Cart cleared"}
