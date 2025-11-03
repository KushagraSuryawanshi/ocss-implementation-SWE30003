"""
Custom exceptions for OCSS business logic.
Provides domain-specific error types for better error handling.
"""

class InsufficientStockError(Exception):
    """Raised when trying to reserve more stock than available."""
    pass

class PaymentDeclinedError(Exception):
    """Raised when payment processing fails."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
    pass

class CartEmptyError(Exception):
    """Raised when trying to checkout with empty cart."""
    pass
