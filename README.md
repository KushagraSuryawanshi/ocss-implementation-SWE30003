# Online Convenience Store System (OCSS)

A command-line based convenience store management system built with Python. This project implements a layered architecture with proper OOP design patterns for managing customers, products, orders, and staff operations.

## Project Overview

OCSS is a comprehensive store management system that supports:
- Customer shopping and checkout
- Staff order fulfillment and inventory management
- Session-based authentication
- Sales reporting and analytics

## Features

### Customer Operations
- Browse product catalog with category filtering
- Add/remove items from shopping cart
- Checkout with payment processing (Card/Wallet)
- View order invoices
- Track order shipping status with tracking number
- Session management

### Staff Operations
- View pending orders
- Ship orders with tracking numbers
- Manage order fulfillment workflow
- Update product inventory
- Generate sales reports (daily/monthly/all-time)

### System Capabilities
- Role-based access control (Customer/Staff)
- Real-time inventory tracking
- Persistent data storage using JSON
- Input validation and error handling
- Comprehensive test coverage

## Architecture

The system follows a **Layered (N-Tier) Architecture**:

```
┌─────────────────────────────────┐
│   Presentation Layer            │
│   - CLI (Typer)                 │
│   - Controllers                 │
│   - Formatters (Rich)           │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Business Logic Layer          │
│   - Domain Models               │
│   - Services                    │
│   - Business Rules              │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Data Access Layer             │
│   - Storage Manager             │
│   - Session Manager             │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Persistence Layer             │
│   - JSON Files                  │
└─────────────────────────────────┘
```

### Design Patterns Used
- **Singleton Pattern**: Inventory management (single source of truth for stock)
- **Factory Pattern**: Payment processing (creates Card/Wallet payment objects)
- **Strategy Pattern**: Report generation (interchangeable reporting algorithms)

## Project Structure

```
ocss-implementation/
├── business/               # Business logic layer
│   ├── models/            # Domain models (Customer, Order, Product, etc.)
│   ├── services/          # Business services (Cart, Order, Auth, etc.)
│   └── exceptions/        # Custom exception classes
├── presentation/          # Presentation layer
│   ├── cli_controller.py  # Main controller
│   └── formatters.py      # Display formatting (Rich tables)
├── storage/               # Data access layer
│   ├── storage_manager.py # CRUD operations
│   ├── json_handler.py    # JSON file I/O
│   └── session_manager.py # User session handling
├── data/                  # JSON data files (auto-created)
│   ├── customers.json
│   ├── products.json
│   ├── orders.json
│   └── ...
├── tests/                 # Test suite
│   └── test_complete_system.py
├── main.py               # Application entry point
├── app_config.py         # Configuration constants
└── requirements.txt      # Python dependencies
```

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Installation

### 1. Clone or Extract the Project

```bash
cd ocss-implementation
```

### 2. Create a Virtual Environment 

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages are:
- `typer==0.12.3` - CLI framework
- `rich==13.7.0` - Terminal formatting
- `pydantic==2.5.3` - Data validation
- `pytest==7.4.3` - Testing framework

## Setup

Before first use, initialize the system with sample data:

```bash
python main.py init
```

This creates:
- 3 sample products (Milk, Bread, Eggs)
- 1 customer account (username: `customer1`, password: `Password123!`)
- 1 staff account (username: `staff1`, password: `Admin123!`)
- Initial inventory levels

## Usage

### Authentication

**Login as Customer:**
```bash
python main.py login customer1 Password123!
```

**Login as Staff:**
```bash
python main.py login staff1 Admin123!
```

**Check Current User:**
```bash
python main.py whoami
```

**Logout:**
```bash
python main.py logout
```

### Customer Commands

**Browse Products:**
```bash
# View all products
python main.py browse

# Filter by category
python main.py browse Dairy
```

**Manage Shopping Cart:**
```bash
# Add item to cart (product_id, quantity)
python main.py add-to-cart 1 2

# View cart
python main.py view-cart
```

**Checkout:**
```bash
python main.py checkout
# You'll be prompted to select payment method (1=Card, 2=Wallet)
```

**View Invoice:**
```bash
python main.py view-invoice 1
```

### Staff Commands

**View Orders:**
```bash
python main.py view-orders
```

**Ship Order:**
```bash
python main.py ship-order 1 TRACK123
```

**Update Inventory:**
```bash
python main.py update-stock 1 100
```

**Generate Reports:**
```bash
python main.py generate-report daily
python main.py generate-report monthly
python main.py generate-report all
```

**Check Order Status:**
```bash
python main.py order-status 1
```

## Complete Workflow Example

**For a clean demonstration, start fresh:**

```bash

# 1. Initialize system with sample data
python main.py init

# 2. Login as customer
python main.py login customer1 Password123!

# 3. Browse products
python main.py browse

# 4. Add items to cart
python main.py add-to-cart 1 2  # 2x Milk
python main.py add-to-cart 2 3  # 3x Bread

# 5. View cart
python main.py view-cart

# 6. Checkout (select 1 for Card when prompted)
python main.py checkout

# 7. View invoice (Order ID will be 1 for first order)
python main.py view-invoice 1

# 8. Logout
python main.py logout

# 9. Login as staff
python main.py login staff1 Admin123!

# 10. View pending orders
python main.py view-orders

# 11. Ship the order
python main.py ship-order 1 TRACK123

# 12. Verify order status
python main.py order-status 1

# 13. Update inventory
python main.py update-stock 1 100
python main.py update-stock 2 50

# 14. Generate sales report
python main.py generate-report daily

# 15. Logout
python main.py logout
```

**Note:** This workflow demonstrates all system capabilities in one sequence. In normal usage, you wouldn't need to delete the data folder - it's only suggested here to ensure the example runs cleanly from start to finish. The "Order not yet paid" error could occur in step 11 if you've run this complete demo multiple times without resetting the data.


## Running Tests

The project includes a comprehensive test suite with 34 tests covering all major functionality.

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_complete_system.py -v
```

**Expected output:**
```
34 passed in ~1.5s
```

## Data Storage

All data is stored in JSON files in the `data/` directory:

- `customers.json` - Customer records
- `accounts.json` - User authentication
- `products.json` - Product catalog
- `inventory.json` - Stock levels
- `orders.json` - Order history
- `invoices.json` - Billing records
- `payments.json` - Payment transactions
- `shipments.json` - Shipping details
- `carts.json` - Shopping carts
- `staff.json` - Staff records

**Note:** The `data/` directory is automatically created when you run `python main.py init`.

## Business Rules

### Validation Rules
- Passwords must be at least 8 characters
- Cart cannot exceed 50 items
- Stock cannot be negative
- Quantities must be positive integers

### Stock Management
- Stock is **not** deducted when adding to cart
- Stock is **reserved** during checkout
- Stock is **permanently deducted** on successful payment
- Stock is **released** if checkout fails

### Order States
1. **PENDING** - Order created, not yet paid
2. **PAID** - Payment processed, awaiting shipment
3. **SHIPPED** - Order dispatched with tracking

## Key Design Decisions

### 1. Decimal for Money
All monetary values use Python's `Decimal` type instead of `float` to avoid floating-point precision errors:

```python
# Float would give: 3.5 * 2 + 4.2 * 3 = 19.600000000000005
# Decimal gives:    3.5 * 2 + 4.2 * 3 = 19.60 (exact)
```

### 2. Domain Objects over Dicts
Cart items and order items are proper objects (`CartItem`, `OrderItem`) rather than dictionaries, providing:
- Type safety
- Encapsulation of business logic
- Ability to add methods and behavior

### 3. Bidirectional Object References
`Customer ↔ Account` and `Staff ↔ Account` use bidirectional references for direct object navigation without database lookups.

### 4. Singleton Inventory
A single `Inventory` instance ensures consistent stock levels across all services, preventing race conditions.

## Coding Standards

This project follows **PEP 8** (Python Enhancement Proposal 8) style guidelines:
- 4 spaces for indentation
- Maximum line length: 100 characters
- Snake_case for functions and variables
- PascalCase for class names
- UPPER_CASE for constants
- Type hints on all function signatures
- Docstrings for all classes and public methods

Reference: https://peps.python.org/pep-0008/

## Development Environment

**Developed and tested on:**
- Operating System: Windows 11
- Python Version: 3.12.10
- IDE: Visual Studio Code

**Compatible with:**
- Windows 10/11
- macOS 12+



## Limitations

- Payment processing is **simulated** (no actual banking integration)
- Single-user sessions (one user at a time)
- No concurrent access handling (single-threaded)
- No database (uses JSON files)
- Command-line interface only (no GUI)

## Future Enhancements

Potential improvements for future versions:
- Web-based UI (Flask/Django)
- Multi-user concurrent access
- Real payment gateway integration
- Product images and descriptions
- Customer reviews and ratings
- Shopping cart persistence across sessions
- Order cancellation and refunds
- Email notifications
- Database backend (PostgreSQL/MySQL)

## Acknowledgments

- **Typer** - Modern CLI framework by Sebastián Ramírez
- **Rich** - Beautiful terminal formatting by Will McGugan
- **pytest** - Python testing framework

---

## Quick Reference Card

### Customer Quick Commands
```bash
python main.py login customer1 Password123!
python main.py browse
python main.py add-to-cart 1 2
python main.py view-cart
python main.py checkout
python main.py logout
```

### Staff Quick Commands
```bash
python main.py login staff1 Admin123!
python main.py view-orders
python main.py ship-order 1 TRACK123
python main.py update-stock 1 100
python main.py generate-report daily
python main.py logout
```

---
