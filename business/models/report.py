"""
File: report.py
Layer: Business Logic
Component: Domain Model - Report (Strategy)
Description:
    Reporting strategies for daily, monthly, and all-time summaries.
    Aggregates orders/payments to produce simple metrics for CLI output.
"""
from typing import List, Dict
from datetime import datetime
from storage.storage_manager import StorageManager

class ReportStrategy:
    def generate(self) -> List[Dict]:
        raise NotImplementedError

class DailyReportStrategy(ReportStrategy):
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        today = datetime.now().date().isoformat()
        todays = [o for o in orders if o["created_at"][:10] == today]
        revenue = sum(float(o["total"]) for o in todays)
        return [
            {"metric": "Report Type", "value": "Daily"},
            {"metric": "Orders Today", "value": len(todays)},
            {"metric": "Revenue Today", "value": round(revenue, 2)},
        ]

class MonthlyReportStrategy(ReportStrategy):
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        ym = datetime.now().strftime("%Y-%m")
        month_orders = [o for o in orders if o["created_at"][:7] == ym]
        revenue = sum(float(o["total"]) for o in month_orders)
        return [
            {"metric": "Report Type", "value": "Monthly"},
            {"metric": "Orders This Month", "value": len(month_orders)},
            {"metric": "Revenue This Month", "value": round(revenue, 2)},
        ]

class AllTimeReportStrategy(ReportStrategy):
    def generate(self) -> List[Dict]:
        s = StorageManager()
        orders = s.load("orders")
        revenue = sum(float(o["total"]) for o in orders)
        return [
            {"metric": "Report Type", "value": "All-Time"},
            {"metric": "Total Orders", "value": len(orders)},
            {"metric": "Total Revenue", "value": round(revenue, 2)},
        ]

class Report:
    def __init__(self, strategy: ReportStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: ReportStrategy) -> None:
        self.strategy = strategy

    def generate_report(self) -> List[Dict]:
        return self.strategy.generate()
