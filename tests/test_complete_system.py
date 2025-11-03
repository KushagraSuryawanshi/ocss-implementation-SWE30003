"""
===============================================================================
File: tests/test_complete_system.py
Description:
    Comprehensive integration tests for OCSS.
    Tests all major workflows: authentication, cart, checkout, staff ops.
    
Run with: pytest tests/test_complete_system.py -v
===============================================================================
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
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


@pytest.fixture(scope="function")
def clean_data_files():
    """Remove all JSON files before each test for clean state"""
    data_dir = Path("data")
    if data_dir.exists():
        for json_file in data_dir.glob("*.json"):
            json_file.unlink()
    yield
    # Cleanup after test
    for json_file in data_dir.glob("*.json"):
        json_file.unlink()


@pytest.fixture
def auth_service(clean_data_files):
    """Initialize auth service with sample data"""
    service = AuthService()
    service.initialize_system()
    return service


@pytest.fixture
def cart_service(auth_service):
    """Cart service fixture"""
    return CartService()


@pytest.fixture
def order_service(auth_service):
    """Order service fixture"""
    return OrderService()


# ============================================================================
# TEST GROUP 1: AUTHENTICATION & SESSION MANAGEMENT
# ============================================================================

def test_customer_login_success(auth_service):
    """Test successful customer login"""
    result = auth_service.login("customer1", "Password123!")
    assert result["success"] == True
    assert result["user"]["user_type"] == "customer"
    assert result["user"]["username"] == "customer1"


def test_staff_login_success(auth_service):
    """Test successful staff login"""
    result = auth_service.login("staff1", "Admin123!")
    assert result["success"] == True
    assert result["user"]["user_type"] == "staff"


def test_login_invalid_credentials(auth_service):
    """Test login with wrong credentials"""
    result = auth_service.login("wronguser", "wrongpass")
    assert result["success"] == False
    assert "Invalid credentials" in result["message"]


def test_logout(auth_service):
    """Test logout clears session"""
    auth_service.login("customer1", "Password123!")
    result = auth_service.logout()
    assert result["success"] == True
    assert auth_service.get_current_user() is None


# ============================================================================
# TEST GROUP 2: PRODUCT & INVENTORY
# ============================================================================

def test_browse_all_products(cart_service):
    """Test browsing all products"""
    products = cart_service.browse_products()
    assert len(products) == 3
    assert products[0]["name"] == "Milk 1L"
    assert products[0]["stock"] == 50


def test_browse_by_category(cart_service):
    """Test filtering products by category"""
    products = cart_service.browse_products(category="Dairy")
    assert len(products) == 2  # Milk and Eggs
    assert all(p["category"] == "Dairy" for p in products)


def test_inventory_singleton(auth_service):
    """Test Inventory Singleton pattern"""
    inv1 = Inventory.get_instance()
    inv2 = Inventory.get_instance()
    assert inv1 is inv2  # Same instance


def test_inventory_stock_check(auth_service):
    """Test checking stock levels"""
    inv = Inventory.get_instance()
    stock = inv.check_stock(1)  # Milk
    assert stock == 50


def test_inventory_reserve_stock(auth_service):
    """Test reserving stock"""
    inv = Inventory.get_instance()
    initial = inv.check_stock(1)
    inv.reserve_stock(1, 5)
    assert inv.check_stock(1) == initial - 5


def test_inventory_insufficient_stock(auth_service):
    """Test error when insufficient stock"""
    inv = Inventory.get_instance()
    with pytest.raises(InsufficientStockError):
        inv.reserve_stock(1, 9999)


# ============================================================================
# TEST GROUP 3: CART OPERATIONS
# ============================================================================

def test_add_item_to_cart(auth_service, cart_service):
    """Test adding item to cart"""
    result = cart_service.add_item(customer_id=1, product_id=1, qty=2)
    assert result["success"] == True
    assert "Added 2x Milk 1L" in result["message"]


def test_add_invalid_product(auth_service, cart_service):
    """Test adding non-existent product"""
    result = cart_service.add_item(customer_id=1, product_id=999, qty=1)
    assert result["success"] == False
    assert "Product not found" in result["message"]


def test_add_insufficient_stock(auth_service, cart_service):
    """Test adding more than available stock"""
    result = cart_service.add_item(customer_id=1, product_id=1, qty=9999)
    assert result["success"] == False
    assert "available" in result["message"].lower()


def test_view_cart(auth_service, cart_service):
    """Test viewing cart contents"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    cart_service.add_item(customer_id=1, product_id=2, qty=3)
    
    cart_data = cart_service.get_cart(customer_id=1)
    assert len(cart_data["items"]) == 2
    assert cart_data["total"] == (2 * 3.5) + (3 * 4.2)  # Milk + Bread


def test_cart_quantity_update(auth_service, cart_service):
    """Test updating item quantity in cart"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    cart_service.add_item(customer_id=1, product_id=1, qty=3)  # Add more
    
    cart_data = cart_service.get_cart(customer_id=1)
    milk_item = next(i for i in cart_data["items"] if i["product_id"] == 1)
    assert milk_item["qty"] == 5  # Should be 2 + 3


def test_view_empty_cart(auth_service, cart_service):
    """Test viewing empty cart"""
    cart_data = cart_service.get_cart(customer_id=1)
    assert cart_data["items"] == []
    assert cart_data["total"] == 0.0


# ============================================================================
# TEST GROUP 4: CHECKOUT & ORDER CREATION
# ============================================================================

def test_checkout_success(auth_service, cart_service, order_service):
    """Test successful checkout"""
    # Add items to cart
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    
    # Checkout
    result = order_service.create_order(customer_id=1)
    
    assert result["success"] == True
    assert result["order_id"] == 1
    assert result["total"] == 7.0  # 2 * 3.5


def test_checkout_empty_cart(auth_service, order_service):
    """Test checkout with empty cart"""
    with pytest.raises(CartEmptyError):
        order_service.create_order(customer_id=1)


def test_checkout_reduces_inventory(auth_service, cart_service, order_service):
    """Test that checkout reduces stock"""
    inv = Inventory.get_instance()
    initial_stock = inv.check_stock(1)
    
    # Add to cart and checkout
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    order_service.create_order(customer_id=1)
    
    # Verify stock reduced
    assert inv.check_stock(1) == initial_stock - 2


def test_checkout_clears_cart(auth_service, cart_service, order_service):
    """Test that checkout clears the cart"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    order_service.create_order(customer_id=1)
    
    cart_data = cart_service.get_cart(customer_id=1)
    assert cart_data["items"] == []


def test_checkout_creates_invoice(auth_service, cart_service, order_service):
    """Test that checkout creates invoice"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    result = order_service.create_order(customer_id=1)
    
    # Check invoice created
    storage = StorageManager()
    invoices = storage.load("invoices")
    assert len(invoices) == 1
    assert invoices[0]["order_id"] == result["order_id"]
    assert invoices[0]["paid"] == True


def test_checkout_creates_payment(auth_service, cart_service, order_service):
    """Test that checkout creates payment record (Factory Method pattern)"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    result = order_service.create_order(customer_id=1)
    
    # Check payment created
    storage = StorageManager()
    payments = storage.load("payments")
    assert len(payments) == 1
    assert payments[0]["order_id"] == result["order_id"]
    assert payments[0]["status"] == "APPROVED"


# ============================================================================
# TEST GROUP 5: STAFF OPERATIONS
# ============================================================================

def test_ship_order_success(auth_service, cart_service, order_service):
    """Test staff shipping an order"""
    # Create order first
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    order_result = order_service.create_order(customer_id=1)
    
    # Ship order
    ship_result = order_service.ship_order(order_result["order_id"], "TRACK123")
    assert ship_result["success"] == True


def test_ship_nonexistent_order(auth_service, order_service):
    """Test shipping non-existent order"""
    result = order_service.ship_order(999, "TRACK123")
    assert result["success"] == False
    assert "not found" in result["message"]


# ============================================================================
# TEST GROUP 6: REPORTING (Strategy Pattern)
# ============================================================================

def test_daily_report(auth_service, cart_service, order_service):
    """Test daily report generation (Strategy pattern)"""
    # Create an order
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    order_service.create_order(customer_id=1)
    
    # Generate daily report
    report_service = ReportService()
    report = report_service.generate("daily")
    
    assert len(report) > 0
    assert any(r["metric"] == "Report Type" and r["value"] == "Daily" for r in report)


def test_monthly_report(auth_service):
    """Test monthly report generation"""
    report_service = ReportService()
    report = report_service.generate("monthly")
    
    assert len(report) > 0
    assert any(r["metric"] == "Report Type" and r["value"] == "Monthly" for r in report)


def test_all_time_report(auth_service):
    """Test all-time report generation"""
    report_service = ReportService()
    report = report_service.generate("all")
    
    assert len(report) > 0
    assert any(r["metric"] == "Report Type" and r["value"] == "All-Time" for r in report)


# ============================================================================
# TEST GROUP 7: DOMAIN MODEL INTEGRITY
# ============================================================================

def test_customer_order_history(auth_service, cart_service, order_service):
    """Test customer can retrieve order history"""
    # Create multiple orders
    cart_service.add_item(customer_id=1, product_id=1, qty=1)
    order_service.create_order(customer_id=1)
    
    cart_service.add_item(customer_id=1, product_id=2, qty=1)
    order_service.create_order(customer_id=1)
    
    # Check order history
    customer = Customer.find_by_id(1)
    history = customer.order_history()
    assert len(history) == 2


def test_product_find_by_id(auth_service):
    """Test finding product by ID"""
    product = Product.find_by_id(1)
    assert product is not None
    assert product.name == "Milk 1L"
    assert product.price == 3.5


def test_order_persistence(auth_service, cart_service, order_service):
    """Test order data persists correctly"""
    cart_service.add_item(customer_id=1, product_id=1, qty=2)
    result = order_service.create_order(customer_id=1)
    
    # Retrieve order
    order = Order.find_by_id(result["order_id"])
    assert order is not None
    assert order.customer_id == 1
    assert order.total == 7.0
    assert order.status == "PAID"


# ============================================================================
# TEST GROUP 8: DESIGN PATTERNS VALIDATION
# ============================================================================

def test_singleton_pattern_inventory(auth_service):
    """Verify Singleton pattern for Inventory"""
    # Get multiple instances
    inv1 = Inventory.get_instance()
    inv2 = Inventory.get_instance()
    inv3 = Inventory()
    
    # All should be same instance
    assert inv1 is inv2
    assert inv2 is inv3


def test_factory_method_payment(auth_service, cart_service, order_service):
    """Verify Factory Method pattern creates correct payment type"""
    cart_service.add_item(customer_id=1, product_id=1, qty=1)
    order_service.create_order(customer_id=1)
    
    storage = StorageManager()
    payments = storage.load("payments")
    
    # Factory should create card payment by default
    assert payments[0]["method"] == "card"


def test_strategy_pattern_reports(auth_service):
    """Verify Strategy pattern allows different report types"""
    report_service = ReportService()
    
    daily = report_service.generate("daily")
    monthly = report_service.generate("monthly")
    all_time = report_service.generate("all")
    
    # Each strategy produces different report type
    assert daily[0]["value"] == "Daily"
    assert monthly[0]["value"] == "Monthly"
    assert all_time[0]["value"] == "All-Time"

def test_staff_update_stock(auth_service):
    service = auth_service
    from business.services.staff_service import StaffService
    staff_service = StaffService()
    result = staff_service.update_stock(1, 99)
    assert result["success"]


# ============================================================================
# RUN SUMMARY
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])