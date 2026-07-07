# utils/export_manager.py
from typing import List, Union, Optional
from .result_formatter import ResultFormatter
from core.base.scan_result import ScanResult

class ExportManager:
    def __init__(self, formatter: ResultFormatter = None):
        self.formatter = formatter or ResultFormatter()

    def export_all(
        self,
        results: List[Union[ScanResult, dict]],
        username: str,
        category: Optional[str] = None
    ):
        
        if not results:
            return
        self.formatter.export_csv_per_platform(results, username, category)
        self.formatter.export_excel_summary(results, username, category)
        out_path = self.formatter._get_user_dir(username, category)
        print(f"[ExportManager] Data untuk '{username}' disimpan ke {out_path}")

    def export_and_display(
        self,
        results: List[Union[ScanResult, dict]],
        title: str,
        username: str,
        category: Optional[str] = None
    ):
        
        self.formatter.display_full_report(
            results, title, username=username, category=category, export=True
        )