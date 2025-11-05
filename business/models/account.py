"""
Defines the Account class used for handling login credentials and linking
accounts with customers or staff members in the system.
"""
from typing import Optional, Dict, TYPE_CHECKING
from storage.storage_manager import StorageManager

# Avoid circular imports
if TYPE_CHECKING:
    from business.models.customer import Customer
    from business.models.staff import Staff

class Account:
    def __init__(self, id: int, username: str, password: str, user_type: str):
        """Initializes a new account record."""
        self.id = id
        self.username = username
        self.password = password
        self.user_type = user_type  # kept for backward compatibility
        
        # Object links
        self._customer: Optional['Customer'] = None
        self._staff: Optional['Staff'] = None

    def verify(self, password: str) -> bool:
        """Checks if the provided password matches this account."""
        return self.password == password

    # --- Collaborator linking methods ---
    
    def set_customer(self, customer: 'Customer') -> None:
        """Links this account to a Customer object."""
        self._customer = customer
        self.user_type = 'customer'

    def set_staff(self, staff: 'Staff') -> None:
        """Links this account to a Staff object."""
        self._staff = staff
        self.user_type = 'staff'

    def get_customer(self) -> Optional['Customer']:
        """Returns the linked Customer object, if any."""
        return self._customer

    def get_staff(self) -> Optional['Staff']:
        """Returns the linked Staff object, if any."""
        return self._staff

    def get_linked_id(self) -> Optional[int]:
        """Returns the ID of the linked Customer or Staff."""
        if self._customer:
            return self._customer.id
        if self._staff:
            return self._staff.id
        return None

    # ---------- Persistence ----------
    
    def to_dict(self) -> Dict:
        """Converts this object to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "user_type": self.user_type,
            "customer_id": self._customer.id if self._customer else None,
            "staff_id": self._staff.id if self._staff else None,
        }

    @staticmethod
    def from_dict(data: Dict) -> "Account":
        """Creates an Account object from stored data."""
        acc = Account(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            user_type=data["user_type"]
        )
        return acc

    @staticmethod
    def find_by_username(username: str) -> Optional["Account"]:
        """Finds and returns an account by username, if it exists."""
        s = StorageManager()
        for row in s.load("accounts"):
            if row["username"] == username:
                return Account.from_dict(row)
        return None

    @staticmethod
    def add(username: str, password: str, user_type: str) -> "Account":
        """Creates and stores a new account record."""
        s = StorageManager()
        rec = s.add("accounts", {
            "username": username,
            "password": password,
            "user_type": user_type,
            "customer_id": None,
            "staff_id": None,
        })
        return Account.from_dict(rec)
    
    def __repr__(self):
        return f"Account(id={self.id}, username={self.username}, type={self.user_type})"