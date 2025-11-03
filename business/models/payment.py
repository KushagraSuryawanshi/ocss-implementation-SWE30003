"""
File: payment.py
Layer: Business Logic
Component: Domain Model - Payment (Factory Method)
Description:
    Abstract payment with concrete mock types. Factory creates the right type.
    On process(), a record is persisted to payments.json.
"""
import random
from typing import Dict
from storage.storage_manager import StorageManager

class PaymentDeclinedError(Exception):
    pass

class Payment:
    def __init__(self, method: str, amount: float, order_id: int):
        self.method = method
        self.amount = float(amount)
        self.order_id = order_id

    def process(self) -> str:
        raise NotImplementedError

    def _persist(self, status: str) -> Dict:
        s = StorageManager()
        return s.add("payments", {
            "order_id": self.order_id,
            "method": self.method,
            "amount": self.amount,
            "status": status
        })

class CardPayment(Payment):
    def process(self) -> str:
        self._persist("APPROVED")
        return "Card payment processed"

class WalletPayment(Payment):
    def process(self) -> str:
        self._persist("APPROVED")
        return "Wallet payment processed"

class PaymentFactory:
    @staticmethod
    def create(method: str, amount: float, order_id: int) -> Payment:
        m = method.lower()
        if m == "card":
            return CardPayment("card", amount, order_id)
        if m == "wallet":
            return WalletPayment("wallet", amount, order_id)
        raise ValueError("Unsupported payment method")
