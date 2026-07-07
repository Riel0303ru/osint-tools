from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt

console = Console()


def show_banner():
    """
    Menampilkan banner utama aplikasi OSINT Fusion.
    """
    title = Text()
    title.append("OSINT FUSION\n", style="bold cyan")
    title.append("Advanced Intelligence Gathering Toolkit", style="white")

    banner = Panel(
        Align.center(title),
        border_style="cyan",
        padding=(1, 4),
        title="[bold green]MAIN MENU[/bold green]",
        subtitle="Python OSINT Framework"
    )

    console.print(banner)


def show_menu():
    """
    Menampilkan daftar menu utama.
    """
    console.print("\n[bold yellow]Pilih modul yang ingin dijalankan:[/bold yellow]\n")
    console.print("[cyan]1.[/cyan] Username Intelligence")
    console.print("[cyan]2.[/cyan] Email Intelligence")
    console.print("[cyan]3.[/cyan] Domain / IP Recon")
    console.print("[cyan]4.[/cyan] Phone Intelligence")
    console.print("[cyan]5.[/cyan] Image Intelligence")
    console.print("[cyan]6.[/cyan] AI Summary")
    console.print("[cyan]7.[/cyan] Relationship Graph")
    console.print("[cyan]8.[/cyan] Export Report")
    console.print("[cyan]0.[/cyan] Exit\n")


def handle_choice(choice: str):
    """
    Menangani pilihan user dari menu utama.
    """
    if choice == "1":
        console.print("\n[green]Username Intelligence belum dibuat.[/green]")
    elif choice == "2":
        console.print("\n[green]Email Intelligence belum dibuat.[/green]")
    elif choice == "3":
        console.print("\n[green]Domain / IP Recon belum dibuat.[/green]")
    elif choice == "4":
        console.print("\n[green]Phone Intelligence belum dibuat.[/green]")
    elif choice == "5":
        console.print("\n[green]Image Intelligence belum dibuat.[/green]")
    elif choice == "6":
        console.print("\n[green]AI Summary belum dibuat.[/green]")
    elif choice == "7":
        console.print("\n[green]Relationship Graph belum dibuat.[/green]")
    elif choice == "8":
        console.print("\n[green]Export Report belum dibuat.[/green]")
    elif choice == "0":
        console.print("\n[bold red]Keluar dari aplikasi...[/bold red]")
        return False
    else:
        console.print("\n[bold red]Pilihan tidak valid.[/bold red]")

    return True


def run_menu():
    """
    Menjalankan menu utama secara loop.
    """
    while True:
        console.clear()
        show_banner()
        show_menu()

        choice = Prompt.ask("Masukkan pilihan", default="0")
        keep_running = handle_choice(choice)

        if not keep_running:
            break

        Prompt.ask("\nTekan Enter untuk kembali ke menu")


if __name__ == "__main__":
    run_menu()