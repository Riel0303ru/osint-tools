# core/report/pdf_converter.py
from pathlib import Path
import os
import subprocess


class PDFConverter:
    """Konversi HTML ke PDF menggunakan pdfkit (wkhtmltopdf)."""

    @staticmethod
    def _find_wkhtmltopdf() -> str:
        """Cari path wkhtmltopdf.exe secara otomatis."""
        # 1. Cek di PATH
        try:
            result = subprocess.run(
                ["where", "wkhtmltopdf"], capture_output=True, text=True, shell=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass

        # 2. Cek di lokasi umum
        common_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\wkhtmltopdf\bin\wkhtmltopdf.exe"),
        ]
        for p in common_paths:
            if os.path.isfile(p):
                return p
        return ""

    @staticmethod
    def convert(html_path: Path, pdf_path: Path) -> bool:
        try:
            import pdfkit

            # Cari wkhtmltopdf
            wk_path = PDFConverter._find_wkhtmltopdf()

            if wk_path:
                config = pdfkit.configuration(wkhtmltopdf=wk_path)
                pdfkit.from_file(str(html_path), str(pdf_path), configuration=config)
                return True
            else:
                # Coba tanpa konfigurasi (mungkin ada di PATH)
                pdfkit.from_file(str(html_path), str(pdf_path))
                return True

        except ImportError:
            print("[WARNING] pdfkit belum terinstal. Jalankan: pip install pdfkit")
            return False
        except OSError as e:
            print(f"[WARNING] wkhtmltopdf tidak ditemukan. Unduh dari https://wkhtmltopdf.org/downloads.html")
            print(f"[INFO] Cek apakah wkhtmltopdf.exe ada di C:\\Program Files\\wkhtmltopdf\\bin\\")
            print(f"[ERROR] Detail: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] PDF conversion failed: {e}")
            return False