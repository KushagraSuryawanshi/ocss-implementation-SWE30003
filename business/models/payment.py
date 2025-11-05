"""
Handles customer payments for orders.
Implements a simple factory pattern to create different payment types.
Uses Decimal for all money calculations for accuracy.
"""

from typing import Dict
from decimal import Decimal
from storage.storage_manager import StorageManager


class PaymentDeclinedError(Exception):
    """Raised when a payment attempt fails."""
    pass


class Payment:
    """Base class for all payment types."""

    def __init__(self, method: str, amount, order_id: int):
        self.method = method
        self.amount = Decimal(str(amount))
        self.order_id = order_id

    def process(self) -> str:
        """Subclasses must implement their own payment process."""
        raise NotImplementedError

    def _persist(self, status: str) -> Dict:
        """Saves a payment record to JSON storage."""
        s = StorageManager()
        return s.add("payments", {
            "order_id": self.order_id,
            "method": self.method,
            "amount": float(self.amount),
            "status": status
        })

    def _persist_result(self, ok: bool) -> str:
        """Returns status text from a boolean flag."""
        return "APPROVED" if ok else "DECLINED"


class CardPayment(Payment):
    """Simulated card payment."""

    def process(self) -> str:
        status = self._persist_result(True)
        self._persist(status)
        return "Card payment processed"


class WalletPayment(Payment):
    """Simulated wallet payment."""

    def process(self) -> str:
        status = self._persist_result(True)
        self._persist(status)
        return "Wallet payment processed"


class PaymentFactory:
    """Factory for creating specific payment objects."""

    @staticmethod
    def create(method: str, amount, order_id: int) -> Payment:
        method = method.lower()
        if method == "card":
            return CardPayment("card", amount, order_id)
        if method == "wallet":
            return WalletPayment("wallet", amount, order_id)
        raise ValueError(f"Unsupported payment method: {method}")
