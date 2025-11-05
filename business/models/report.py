"""
Implements different reporting strategies for the store.
Each strategy summarizes sales over a specific time period:
daily, monthly, or all-time.
"""

from typing import List, Dict
from datetime import datetime
from storage.storage_manager import StorageManager


class ReportStrategy:
    """Base class for all reporting strategies."""
    def generate(self) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement this method.")


class DailyReportStrategy(ReportStrategy):
    """Generates a report for the current day's sales."""
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        today = datetime.now().date().isoformat()

        todays_orders = [o for o in orders if o["created_at"][:10] == today]
        revenue = sum(float(o["total"]) for o in todays_orders)

        return [
            {"metric": "Report Type", "value": "Daily"},
            {"metric": "Orders Today", "value": len(todays_orders)},
            {"metric": "Revenue Today", "value": f"{revenue:.2f}"},
        ]


class MonthlyReportStrategy(ReportStrategy):
    """Generates a report for the current month."""
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        current_month = datetime.now().strftime("%Y-%m")

        month_orders = [o for o in orders if o["created_at"][:7] == current_month]
        revenue = sum(float(o["total"]) for o in month_orders)

        return [
            {"metric": "Report Type", "value": "Monthly"},
            {"metric": "Orders This Month", "value": len(month_orders)},
            {"metric": "Revenue This Month", "value": f"{revenue:.2f}"},
        ]


class AllTimeReportStrategy(ReportStrategy):
    """Generates a summary of all-time sales data."""
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        revenue = sum(float(o["total"]) for o in orders)

        return [
            {"metric": "Report Type", "value": "All-Time"},
            {"metric": "Total Orders", "value": len(orders)},
            {"metric": "Total Revenue", "value": f"{revenue:.2f}"},

        ]


class Report:
    """Context class that uses a reporting strategy to generate results."""

    def __init__(self, strategy: ReportStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: ReportStrategy) -> None:
        """Switches to a different reporting strategy."""
        self.strategy = strategy

    def generate_report(self) -> List[Dict]:
        """Runs the active report strategy."""
        return self.strategy.generate()
