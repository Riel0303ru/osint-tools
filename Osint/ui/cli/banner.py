from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table

from utils.config_manager import ConfigManager

console = Console()


class BannerUI:
    """
    Menangani seluruh tampilan banner dan informasi startup UI.
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        self.project_name = self.config.get("project_name", "OSINT Fusion")
        self.version = self.config.get("version", "1.0")

        self.theme = self.config.get("theme", {})
        self.primary_color = self.theme.get("primary_color", "cyan")
        self.secondary_color = self.theme.get("secondary_color", "green")

    def show_main_banner(self):
        """
        Menampilkan banner utama aplikasi.
        """

        title = Text()

        title.append(
            f"{self.project_name}\n",
            style=f"bold {self.primary_color}"
        )

        title.append(
            "Advanced Intelligence Gathering Framework",
            style="white"
        )

        banner = Panel(
            Align.center(title),
            border_style=self.primary_color,
            padding=(1, 4),
            title=f"[bold {self.secondary_color}]SYSTEM ONLINE[/bold {self.secondary_color}]",
            subtitle=f"Version {self.version}"
        )

        console.print(banner)

    def show_system_info(self):
        """
        Menampilkan informasi system startup.
        """

        info_table = Table(
            title="[bold cyan]System Status[/bold cyan]",
            border_style=self.primary_color
        )

        info_table.add_column("Component", style="bold white")
        info_table.add_column("Status", style="green")

        info_table.add_row("Core Engine", "LOADED")
        info_table.add_row("UI Engine", "LOADED")
        info_table.add_row("Configuration", "LOADED")
        info_table.add_row("Environment", "READY")

        console.print(info_table)

    def show_startup_screen(self):
        """
        Menampilkan keseluruhan tampilan startup.
        """

        console.clear()

        self.show_main_banner()

        console.print()

        self.show_system_info()

        console.print(
            f"\n[bold {self.primary_color}]OSINT Fusion is ready.[/bold {self.primary_color}]"
        )