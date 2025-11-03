"""
File: report_service.py
Layer: Business Logic
Component: Report Service
Description:
    Generates sales and order analytics using Strategy Pattern.
"""
from typing import List, Dict
from business.models.report import (
    Report,
    DailyReportStrategy,
    MonthlyReportStrategy,
    AllTimeReportStrategy,
)

class ReportService:
    # generate report based on given period
    def generate(self, period: str) -> List[Dict]:
        p = period.lower()
        if p == "daily":
            strategy = DailyReportStrategy()
        elif p == "monthly":
            strategy = MonthlyReportStrategy()
        else:
            strategy = AllTimeReportStrategy()

        report = Report(strategy)
        return report.generate_report()
