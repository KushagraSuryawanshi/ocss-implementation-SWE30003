from typing import List, Dict, Optional
from storage.storage_manager import StorageManager
from business.models.cart import Cart
from business.models.order import Order
from business.models.invoice import Invoice
from business.models.payment import PaymentFactory
from business.models.inventory import Inventory
from business.exceptions.errors import CartEmptyError, InsufficientStockError

class Customer:
    def __init__(self, id: int, name: str, email: str, address: str):
        # init customer with id, name, email, address
        self.id = id
        self.name = name
        self.email = email
        self.address = address

    # get or create customer's cart
    def get_cart(self) -> Cart:
        return Cart.get_or_create_for_customer(self.id)

    # add product to cart
    def add_to_cart(self, product_id: int, qty: int) -> Dict:
        cart = self.get_cart()
        cart.add_item(product_id, qty)
        return {"success": True, "message": "Cart updated"}

    # clear customer's cart
    def clear_cart(self) -> None:
        self.get_cart().clear()

    # perform checkout flow
    def checkout_via(self, payment_method: str = "card") -> Dict:
        cart = self.get_cart()
        if cart.is_empty():
            raise CartEmptyError("Cannot checkout with empty cart")

        inv = Inventory.get_instance()
        try:
            # reserve stock
            cart.reserve_all()
            
            # create order and invoice
            snap = cart.to_order_snapshot()
            order = Order.create(self.id, snap["items"], snap["total"])
            invoice = Invoice.create(order.id, order.total)

            # process payment
            payment = PaymentFactory.create(payment_method, order.total, order.id)
            payment.process()

            # mark as paid
            invoice.mark_paid()
            order.mark_paid()

            # clear cart after payment
            cart.clear()
            return {
                "success": True,
                "order_id": order.id,
                "invoice_id": invoice.id,
                "total": order.total
            }

        except InsufficientStockError as e:
            # release stock if not enough
            cart.release_all()
            return {"success": False, "message": str(e)}

        except Exception as e:
            # release stock if checkout fails
            cart.release_all()
            return {"success": False, "message": f"Checkout failed: {e}"}

    # convert customer to dict
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
        }

    # create customer from dict
    @staticmethod
    def from_dict(data: Dict) -> "Customer":
        return Customer(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            address=data["address"],
        )

    # add new customer to storage
    @staticmethod
    def add(name: str, email: str, address: str) -> "Customer":
        s = StorageManager()
        rec = s.add("customers", {"name": name, "email": email, "address": address})
        return Customer.from_dict(rec)

    # find customer by id
    @staticmethod
    def find_by_id(customer_id: int) -> Optional["Customer"]:
        s = StorageManager()
        row = s.find_by_id("customers", customer_id)
        return Customer.from_dict(row) if row else None

    # get customer's past orders
    def order_history(self) -> List[Dict]:
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("customer_id") == self.id]
