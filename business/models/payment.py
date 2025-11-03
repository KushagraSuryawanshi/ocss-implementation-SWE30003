"""
File: payment.py
Layer: Business Logic
Component: Domain Model - Payment (Factory Method)
Description:
    Abstract payment with concrete mock types. Factory creates the right type.
    On process(), a record is persisted to payments.json.
"""
from typing import Dict
from storage.storage_manager import StorageManager

class PaymentDeclinedError(Exception):
    # custom exception for declined payments
    pass

class Payment:
    def __init__(self, method: str, amount: float, order_id: int):
        # init payment with method, amount, and order id
        self.method = method
        self.amount = float(amount)
        self.order_id = order_id

    # base process method (to be overridden)
    def process(self) -> str:
        raise NotImplementedError

    # save payment record to storage
    def _persist(self, status: str) -> Dict:
        s = StorageManager()
        return s.add("payments", {
            "order_id": self.order_id,
            "method": self.method,
            "amount": self.amount,
            "status": status
        })

    # return status string based on result
    def _persist_result(self, ok: bool) -> str:
        return "APPROVED" if ok else "DECLINED"

# card payment implementation
class CardPayment(Payment):
    def process(self) -> str:
        status = self._persist_result(True)
        self._persist(status)
        return "Card payment processed"

# wallet payment implementation
class WalletPayment(Payment):
    def process(self) -> str:
        status = self._persist_result(True)
        self._persist(status)
        return "Wallet payment processed"

# payment factory to create proper type
class PaymentFactory:
    @staticmethod
    def create(method: str, amount: float, order_id: int) -> Payment:
        m = method.lower()
        if m == "card":
            return CardPayment("card", amount, order_id)
        if m == "wallet":
            return WalletPayment("wallet", amount, order_id)
        raise ValueError("Unsupported payment method")
