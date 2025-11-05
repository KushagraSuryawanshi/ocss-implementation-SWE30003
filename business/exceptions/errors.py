"""
This file defines custom exception classes used across the OCSS system.
Each class represents a specific kind of business rule or runtime error
that can occur during system operations.
"""

class InsufficientStockError(Exception):
    """Raised when a product does not have enough stock."""
    pass


class PaymentDeclinedError(Exception):
    """Raised when a payment cannot be completed."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when user login details are incorrect."""
    pass


class CartEmptyError(Exception):
    """Raised when checkout is attempted with an empty cart."""
    pass
