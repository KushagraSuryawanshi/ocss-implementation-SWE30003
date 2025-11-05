"""
Comprehensive integration tests for the Online Convenience Store System (OCSS).
Covers login, cart, checkout, inventory, reports, and staff operations.
Run with: pytest -v
"""

import pytest
from pathlib import Path
import sys
from decimal import Decimal

# Allow local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from business.models.customer import Customer
from business.models.product import Product
from business.models.inventory import Inventory
from business.models.cart import Cart
from business.models.order import Order
from business.models.account import Account
from business.services.auth_service import AuthService
from business.services.cart_service import CartService
from business.services.order_service import OrderService
from business.services.report_service import ReportService
from storage.storage_manager import StorageManager
from business.exceptions.errors import InsufficientStockError, CartEmptyError


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture(scope="function")
def clean_data_files():
    """Ensure a clean data directory for each test run."""
    data_dir = Path("data")
    if data_dir.exists():
        for f in data_dir.glob("*.json"):
            f.unlink()
    yield
    for f in data_dir.glob("*.json"):
        f.unlink()


@pytest.fixture
def auth_service(clean_data_files):
    """Initialize sample data and return AuthService."""
    service = AuthService()
    service.initialize_system()
    return service


@pytest.fixture
def cart_service(auth_service):
    return CartService()


@pytest.fixture
def order_service(auth_service):
    return OrderService()


# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------
def test_customer_login_success(auth_service):
    result = auth_service.login("customer1", "Password123!")
    assert result["success"]
    assert result["user"]["user_type"] == "customer"


def test_staff_login_success(auth_service):
    result = auth_service.login("staff1", "Admin123!")
    assert result["success"]
    assert result["user"]["user_type"] == "staff"


def test_login_invalid_credentials(auth_service):
    result = auth_service.login("wronguser", "wrongpass")
    assert not result["success"]
    assert "Invalid credentials" in result["message"]


def test_logout(auth_service):
    auth_service.login("customer1", "Password123!")
    result = auth_service.logout()
    assert result["success"]
    assert auth_service.get_current_user() is None


# ---------------------------------------------------------------------
# Products and Inventory
# ---------------------------------------------------------------------
def test_browse_all_products(cart_service):
    products = cart_service.browse_products()
    assert len(products) == 3
    assert products[0]["name"] == "Milk 1L"


def test_browse_by_category(cart_service):
    products = cart_service.browse_products(category="Dairy")
    assert len(products) == 2
    assert all(p["category"] == "Dairy" for p in products)


def test_inventory_singleton(auth_service):
    inv1 = Inventory.get_instance()
    inv2 = Inventory.get_instance()
    assert inv1 is inv2


def test_inventory_stock_check(auth_service):
    inv = Inventory.get_instance()
    assert inv.check_stock(1) == 50


def test_inventory_reserve_stock(auth_service):
    inv = Inventory.get_instance()
    before = inv.check_stock(1)
    inv.reserve_stock(1, 5)
    assert inv.check_stock(1) == before - 5


def test_inventory_insufficient_stock(auth_service):
    inv = Inventory.get_instance()
    with pytest.raises(InsufficientStockError):
        inv.reserve_stock(1, 9999)


# ---------------------------------------------------------------------
# Cart Operations
# ---------------------------------------------------------------------
def test_add_item_to_cart(auth_service, cart_service):
    result = cart_service.add_item(1, 1, 2)
    assert result["success"]
    assert "Added 2x Milk" in result["message"]


def test_add_invalid_product(auth_service, cart_service):
    result = cart_service.add_item(1, 999, 1)
    assert not result["success"]
    assert "Product not found" in result["message"]


def test_add_insufficient_stock(auth_service, cart_service):
    result = cart_service.add_item(1, 1, 9999)
    assert not result["success"]
    assert "available" in result["message"].lower()


def test_view_cart(auth_service, cart_service):
    cart_service.add_item(1, 1, 2)
    cart_service.add_item(1, 2, 3)
    cart = cart_service.get_cart(1)
    assert len(cart["items"]) == 2
    assert cart["total"] == pytest.approx((2 * 3.5) + (3 * 4.2))


def test_cart_quantity_update(auth_service, cart_service):
    cart_service.add_item(1, 1, 2)
    cart_service.add_item(1, 1, 3)
    cart = cart_service.get_cart(1)
    milk = next(i for i in cart["items"] if i["product_id"] == 1)
    assert milk["qty"] == 5


def test_view_empty_cart(auth_service, cart_service):
    cart = cart_service.get_cart(1)
    assert cart["items"] == []
    assert cart["total"] == 0.0


# ---------------------------------------------------------------------
# Checkout & Orders
# ---------------------------------------------------------------------
def test_checkout_success(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    result = order_service.create_order(1)
    assert result["success"]
    assert result["order_id"] == 1
    assert result["total"] == 7.0


def test_checkout_empty_cart(auth_service, order_service):
    with pytest.raises(CartEmptyError):
        order_service.create_order(1)


def test_checkout_reduces_inventory(auth_service, cart_service, order_service):
    inv = Inventory.get_instance()
    before = inv.check_stock(1)
    cart_service.add_item(1, 1, 2)
    order_service.create_order(1)
    assert inv.check_stock(1) == before - 2


def test_checkout_clears_cart(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    order_service.create_order(1)
    cart = cart_service.get_cart(1)
    assert not cart["items"]


def test_checkout_creates_invoice(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    result = order_service.create_order(1)
    invoices = StorageManager().load("invoices")
    assert invoices and invoices[0]["order_id"] == result["order_id"]
    assert invoices[0]["paid"]


def test_checkout_creates_payment(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    result = order_service.create_order(1)
    payments = StorageManager().load("payments")
    assert payments and payments[0]["order_id"] == result["order_id"]
    assert payments[0]["status"] == "APPROVED"


# ---------------------------------------------------------------------
# Staff Operations
# ---------------------------------------------------------------------
def test_ship_order_success(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    order_result = order_service.create_order(1)
    ship = order_service.ship_order(order_result["order_id"], "TRACK123")
    assert ship["success"]


def test_ship_nonexistent_order(auth_service, order_service):
    result = order_service.ship_order(999, "TRACK123")
    assert not result["success"]
    assert "not found" in result["message"]


# ---------------------------------------------------------------------
# Reporting (Strategy Pattern)
# ---------------------------------------------------------------------
def test_daily_report(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    order_service.create_order(1)
    report = ReportService().generate("daily")
    assert any(r["metric"] == "Report Type" and r["value"] == "Daily" for r in report)


def test_monthly_report(auth_service):
    report = ReportService().generate("monthly")
    assert any(r["value"] == "Monthly" for r in report)


def test_all_time_report(auth_service):
    report = ReportService().generate("all")
    assert any(r["value"] == "All-Time" for r in report)


# ---------------------------------------------------------------------
# Domain Model Integrity
# ---------------------------------------------------------------------
def test_customer_order_history(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 1)
    order_service.create_order(1)
    cart_service.add_item(1, 2, 1)
    order_service.create_order(1)
    history = Customer.find_by_id(1).order_history()
    assert len(history) == 2


def test_product_find_by_id(auth_service):
    p = Product.find_by_id(1)
    assert p and p.name == "Milk 1L"
    assert p.price == Decimal("3.5")


def test_order_persistence(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 2)
    result = order_service.create_order(1)
    order = Order.find_by_id(result["order_id"])
    assert order
    assert order.customer.id == 1
    assert order.total == Decimal("7.0")
    assert order.status == "PAID"


# ---------------------------------------------------------------------
# Design Pattern Validation
# ---------------------------------------------------------------------
def test_singleton_pattern_inventory(auth_service):
    inv1 = Inventory.get_instance()
    inv2 = Inventory.get_instance()
    inv3 = Inventory()
    assert inv1 is inv2 is inv3


def test_factory_method_payment(auth_service, cart_service, order_service):
    cart_service.add_item(1, 1, 1)
    order_service.create_order(1)
    payments = StorageManager().load("payments")
    assert payments[0]["method"] == "card"


def test_strategy_pattern_reports(auth_service):
    r = ReportService()
    assert r.generate("daily")[0]["value"] == "Daily"
    assert r.generate("monthly")[0]["value"] == "Monthly"
    assert r.generate("all")[0]["value"] == "All-Time"


def test_staff_update_stock(auth_service):
    from business.services.staff_service import StaffService
    result = StaffService().update_stock(1, 99)
    assert result["success"]
