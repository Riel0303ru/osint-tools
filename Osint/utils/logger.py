# utils/logger.py
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()


class Logger:

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = Path(base_dir)

        self.logs_dir = self.base_dir / "logs"

        self.system_log = self.logs_dir / "system.log"
        self.error_log  = self.logs_dir / "error.log"

        self._initialize_logger()

    def _initialize_logger(self):
 
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self) -> str:


        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_to_file(self, file_path: Path, message: str):

        with open(file_path, "a", encoding="utf-8") as file:
            file.write(message + "\n")

    # ---------- LEVEL LOG ----------

    def debug(self, message: str):
        timestamp = self._get_timestamp()
        formatted_message = f"[DEBUG] [{timestamp}] {message}"

        console.print(
            f"[dim][DEBUG][/dim] [dim white]{message}[/dim white]"
        )

        # Debug hanya disimpan di system log
        self._write_to_file(self.system_log, formatted_message)

    def info(self, message: str):


        timestamp = self._get_timestamp()

        formatted_message = f"[INFO] [{timestamp}] {message}"

        console.print(
            f"[bold cyan][INFO][/bold cyan] [white]{message}[/white]"
        )

        self._write_to_file(
            self.system_log,
            formatted_message
        )

    def success(self, message: str):
 

        timestamp = self._get_timestamp()

        formatted_message = f"[SUCCESS] [{timestamp}] {message}"

        console.print(
            f"[bold green][SUCCESS][/bold green] [white]{message}[/white]"
        )

        self._write_to_file(
            self.system_log,
            formatted_message
        )

    def warning(self, message: str):


        timestamp = self._get_timestamp()

        formatted_message = f"[WARNING] [{timestamp}] {message}"

        console.print(
            f"[bold yellow][WARNING][/bold yellow] [white]{message}[/white]"
        )

        self._write_to_file(
            self.system_log,
            formatted_message
        )

    def error(self, message: str):
    

        timestamp = self._get_timestamp()

        formatted_message = f"[ERROR] [{timestamp}] {message}"

        console.print(
            f"[bold red][ERROR][/bold red] [white]{message}[/white]"
        )

        self._write_to_file(
            self.system_log,
            formatted_message
        )

        self._write_to_file(
            self.error_log,
            formatted_message
        )

    def critical(self, message: str):

        timestamp = self._get_timestamp()

        formatted_message = f"[CRITICAL] [{timestamp}] {message}"

        console.print(
            f"[bold red on white][CRITICAL][/bold red on white] [bold red]{message}[/bold red]"
        )

        self._write_to_file(
            self.system_log,
            formatted_message
        )

        self._write_to_file(
            self.error_log,
            formatted_message
        )

    def divider(self):

        line = "=" * 60

        console.print(f"[dim]{line}[/dim]")

        self._write_to_file(
            self.system_log,
            line
        )