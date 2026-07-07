# core/image/reverse_search.py
from __future__ import annotations

import webbrowser
from typing import Dict, List

from rich.console import Console

console = Console()

REVERSE_LINKS = {
    "Google Lens": "https://lens.google.com/",
    "Yandex Images": "https://yandex.com/images/",
    "Bing Visual Search": "https://www.bing.com/visualsearch",
    "TinEye": "https://tineye.com",
}


class ReverseSearch:
    """
    Reverse image search launcher.
    Membuka browser secara otomatis ke platform reverse image search.
    """

    @staticmethod
    def search(image_path: str) -> List[Dict]:
        """
        Kembalikan daftar platform dengan URL dan status.
        Tidak melakukan scraping – user cukup upload manual di browser.
        """
        results = []
        for platform, url in REVERSE_LINKS.items():
            results.append(
                {
                    "platform": platform,
                    "status": "READY",
                    "url": url,
                    "message": f"Buka {url} lalu upload gambar secara manual",
                }
            )
        return results

    @staticmethod
    def open_all():
        """
        Buka semua platform reverse image search di browser sekaligus.
        """
        for platform, url in REVERSE_LINKS.items():
            console.print(f"[cyan]Membuka {platform}...[/cyan]")
            webbrowser.open(url)

    @staticmethod
    def open_platform(platform_name: str):
        """
        Buka satu platform tertentu di browser.
        """
        url = REVERSE_LINKS.get(platform_name)
        if url:
            console.print(f"[cyan]Membuka {platform_name}...[/cyan]")
            webbrowser.open(url)
        else:
            console.print(f"[red]Platform '{platform_name}' tidak ditemukan.[/red]")