"""
Generates reports for sales and orders using the Strategy pattern.
Each report type (daily, monthly, all-time) summarizes order data differently.
"""

from typing import List, Dict
from business.models.report import (
    Report,
    DailyReportStrategy,
    MonthlyReportStrategy,
    AllTimeReportStrategy,
)

class ReportService:
    """Selects and runs the appropriate reporting strategy."""

    def generate(self, period: str) -> List[Dict]:
        period = period.lower()

        if period == "daily":
            strategy = DailyReportStrategy()
        elif period == "monthly":
            strategy = MonthlyReportStrategy()
        else:
            strategy = AllTimeReportStrategy()

        report = Report(strategy)
        return report.generate_report()
