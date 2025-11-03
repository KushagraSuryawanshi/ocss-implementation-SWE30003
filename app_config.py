"""
File: app_config.py
Layer: Configuration
Component: Global Configuration
Description:
    Defines system-wide constants and data paths.
    Ensures all JSON persistence files and folders exist before use.
"""
from pathlib import Path

# Root and data directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# JSON data files
CUSTOMERS_FILE = DATA_DIR / "customers.json"
ACCOUNTS_FILE  = DATA_DIR / "accounts.json"
PRODUCTS_FILE  = DATA_DIR / "products.json"
INVENTORY_FILE = DATA_DIR / "inventory.json"
ORDERS_FILE    = DATA_DIR / "orders.json"
INVOICES_FILE  = DATA_DIR / "invoices.json"
PAYMENTS_FILE  = DATA_DIR / "payments.json"
SHIPMENTS_FILE = DATA_DIR / "shipments.json"
CARTS_FILE     = DATA_DIR / "carts.json"
STAFF_FILE     = DATA_DIR / "staff.json"

# Business rules and thresholds
MIN_PASSWORD_LENGTH = 8
MAX_CART_ITEMS      = 50
LOW_STOCK_THRESHOLD = 5
