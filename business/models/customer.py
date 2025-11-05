"""
Defines the Customer class used to represent store customers.
Each customer is linked to an Account object and can manage their own cart,
perform checkouts, and view order history.
"""

from typing import List, Dict, Optional, TYPE_CHECKING
from storage.storage_manager import StorageManager

if TYPE_CHECKING:
    from business.models.account import Account
    from business.models.cart import Cart
    from business.models.order import Order


class Customer:
    def __init__(self, id: int, name: str, email: str, address: str):
        """Initializes a new customer record."""
        self.id = id
        self.name = name
        self.email = email
        self.address = address

        # Reference to the linked Account object
        self._account: Optional['Account'] = None

    # --- Account collaboration ---

    def set_account(self, account: 'Account') -> None:
        """Links this customer to an Account (two-way link)."""
        self._account = account
        account.set_customer(self)

    def get_account(self) -> Optional['Account']:
        """Returns the linked Account object, if any."""
        return self._account

    # --- Cart and Checkout Operations ---

    def get_cart(self) -> 'Cart':
        """Gets or creates a cart for this customer."""
        from business.models.cart import Cart
        return Cart.get_or_create_for_customer(self.id)

    def add_to_cart(self, product_id: int, qty: int) -> Dict:
        """Adds a product to the customer's cart."""
        cart = self.get_cart()
        cart.add_item(product_id, qty)
        return {"success": True, "message": "Cart updated"}

    def clear_cart(self) -> None:
        """Clears all items from the customer's cart."""
        self.get_cart().clear()

    def checkout_via(self, payment_method: str = "card") -> Dict:
        """Handles the full checkout process for the customer."""
        from business.models.cart import Cart
        from business.models.order import Order
        from business.models.invoice import Invoice
        from business.models.payment import PaymentFactory
        from business.models.inventory import Inventory
        from business.exceptions.errors import CartEmptyError, InsufficientStockError

        cart = self.get_cart()
        if cart.is_empty():
            raise CartEmptyError("Cannot checkout with empty cart")

        inv = Inventory.get_instance()
        try:
            # Reserve stock for the order
            cart.reserve_all()

            # Create order and invoice
            snapshot = cart.to_order_snapshot()
            order = Order.create(self.id, snapshot["items"], snapshot["total"])
            invoice = Invoice.create(order.id, order.total)

            # Process payment
            payment = PaymentFactory.create(payment_method, order.total, order.id)
            payment.process()

            # Mark order and invoice as paid
            invoice.mark_paid()
            order.mark_paid()

            # Clear the cart
            cart.clear()

            return {
                "success": True,
                "order_id": order.id,
                "invoice_id": invoice.id,
                "total": order.total
            }

        except InsufficientStockError as e:
            cart.release_all()
            return {"success": False, "message": str(e)}

        except Exception as e:
            cart.release_all()
            return {"success": False, "message": f"Checkout failed: {e}"}

    # --- Persistence ---

    def to_dict(self) -> Dict:
        """Converts this customer into a dictionary for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Customer":
        """Creates a Customer object from stored data."""
        return Customer(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            address=data["address"],
        )

    @staticmethod
    def add(name: str, email: str, address: str) -> "Customer":
        """Adds a new customer record to storage."""
        s = StorageManager()
        rec = s.add("customers", {"name": name, "email": email, "address": address})
        return Customer.from_dict(rec)

    @staticmethod
    def find_by_id(customer_id: int) -> Optional["Customer"]:
        """Finds a customer by ID."""
        s = StorageManager()
        row = s.find_by_id("customers", customer_id)
        return Customer.from_dict(row) if row else None

    def order_history(self) -> List[Dict]:
        """Returns a list of this customer's past orders."""
        s = StorageManager()
        return [o for o in s.load("orders") if o.get("customer_id") == self.id]

    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name}, email={self.email})"
