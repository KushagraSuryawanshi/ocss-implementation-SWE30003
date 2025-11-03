"""
File: account.py
Layer: Business Logic
Component: Domain Model - Account
Description:
    Represents login credentials and role (customer/staff).
    Provides credential verification and simple persistence helpers.
"""
from typing import Optional, Dict
from storage.storage_manager import StorageManager

class Account:
    def __init__(
        self, 
        id: int, 
        username: str, 
        password: str, 
        user_type: str, 
        customer_id: int | None = None, 
        staff_id: int | None = None
    ):
        # init account details
        self.id = id
        self.username = username
        self.password = password  # plain text for now
        self.user_type = user_type  # 'customer' or 'staff'
        self.customer_id = customer_id
        self.staff_id = staff_id

    # verify password
    def verify(self, password: str) -> bool:
        return self.password == password

    # convert account to dict
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "user_type": self.user_type,
            "customer_id": self.customer_id,
            "staff_id": self.staff_id,
        }

    # create account from dict
    @staticmethod
    def from_dict(data: Dict) -> "Account":
        return Account(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            user_type=data["user_type"],
            customer_id=data.get("customer_id"),
            staff_id=data.get("staff_id"),
        )

    # find account by username
    @staticmethod
    def find_by_username(username: str) -> Optional["Account"]:
        s = StorageManager()
        for row in s.load("accounts"):
            if row["username"] == username:
                return Account.from_dict(row)
        return None

    # add a new account to storage
    @staticmethod
    def add(
        username: str, 
        password: str, 
        user_type: str, 
        customer_id: int | None = None, 
        staff_id: int | None = None
    ) -> "Account":
        s = StorageManager()
        rec = s.add("accounts", {
            "username": username,
            "password": password,
            "user_type": user_type,
            "customer_id": customer_id,
            "staff_id": staff_id,
        })
        return Account.from_dict(rec)
