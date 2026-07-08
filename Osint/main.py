# main.py
from __future__ import annotations

import asyncio
import os
import re
import json
from pathlib import Path

# ---------- Load environment dari .env.local ----------
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent / ".env.local"
load_dotenv(dotenv_path=env_path)

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from ui.cli.banner import BannerUI
from core.base.scan_manager import ScanManager
from utils.logger import Logger
from utils.export_manager import ExportManager
from core.username.platforms import PLATFORMS
from core.phone.phone_workflow import PhoneWorkflow
from core.graph.graph_builder import GraphBuilder
from core.graph.graph_visualizer import GraphVisualizer
from core.graph.delta_graph import DeltaGraph
from core.ai.ai_workflow import AIWorkflow
from core.report.report_generator import ReportGenerator
from core.email.email_workflow import EmailWorkflow
from core.username.username_workflow import UsernameWorkflow
from core.domain.domain_workflow import DomainWorkflow
from core.ip.ip_workflow import IPWorkflow
from core.company.company_workflow import CompanyWorkflow
from core.document.document_workflow import DocumentWorkflow
from core.darkweb.darkweb_workflow import DarkwebWorkflow
from core.video.video_workflow import VideoWorkflow

console = Console()


class OSINTFusionApp:
    """
    Main controller OSINT Fusion.
    Semua output tersimpan rapi di dalam Osint/results/.
    """

    def __init__(self):
        self.logger = Logger()
        self.banner = BannerUI()
        self.scan_manager = ScanManager()
        self.export_manager = ExportManager()

        self.phone_workflow = PhoneWorkflow(
            base_dir="Osint",
            storage=self.scan_manager.storage,
            export_manager=self.export_manager,
        )

        self.graph_builder = GraphBuilder(self.scan_manager.storage)
        self.graph_visualizer = None
        self.delta_graph = DeltaGraph(self.scan_manager.storage)

        self.ai_workflow = AIWorkflow()
        self.report_generator = ReportGenerator(self.scan_manager.storage, base_dir="Osint")

        self.email_workflow = EmailWorkflow(base_dir="Osint")
        self.username_workflow = UsernameWorkflow(base_dir="Osint")
        self.domain_workflow = DomainWorkflow(base_dir="Osint")
        self.ip_workflow = IPWorkflow(base_dir="Osint")
        self.company_workflow = CompanyWorkflow(base_dir="Osint")
        self.document_workflow = DocumentWorkflow(base_dir="Osint")
        self.darkweb_workflow = DarkwebWorkflow(base_dir="Osint")
        self.video_workflow = VideoWorkflow(base_dir="Osint")

        self.app_name = "OSINT Fusion"
        self.version = "1.0.0"
        self.running = True

    def initialize(self):
        self.logger.divider()
        self.logger.info(f"Initializing {self.app_name} v{self.version}")
        self.logger.success("Application initialization complete")
        self.logger.divider()

    def pause(self):
        Prompt.ask("\nPress Enter to continue")

    def show_section_title(self, title: str):
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))

    def show_platform_table(self):
        table = Table(title="Available Platforms", border_style="cyan")
        table.add_column("No", justify="center", style="cyan")
        table.add_column("Platform", style="white")
        table.add_column("Priority Hint", style="green")
        priority_set = {"Instagram", "GitHub", "TikTok", "X (Twitter)", "LinkedIn", "Reddit"}
        for i, p in enumerate(PLATFORMS, 1):
            priority = "HIGH" if p["name"] in priority_set else "NORMAL"
            table.add_row(str(i), p["name"], priority)
        console.print(table)

    def show_main_menu(self):
        self.show_section_title("MAIN MENU")
        menu_items = [
            "[cyan][1][/cyan] Username Intelligence",
            "[cyan][2][/cyan] Email Intelligence",
            "[cyan][3][/cyan] Domain Intelligence",
            "[cyan][4][/cyan] Phone Intelligence",
            "[cyan][5][/cyan] Image Intelligence",
            "[cyan][6][/cyan] AI Analysis",
            "[cyan][7][/cyan] Relationship Graph",
            "[cyan][8][/cyan] History & Delta",
            "[cyan][9][/cyan] PDF Report Generator",
            "[cyan][10][/cyan] IP Intelligence",
            "[cyan][11][/cyan] Company Intelligence",
            "[cyan][12][/cyan] Cross-Module Correlation",
            "[cyan][13][/cyan] Document Intelligence",
            "[cyan][14][/cyan] Dark Web Intelligence",
            "[cyan][15][/cyan] Video Intelligence",
            "[cyan][0][/cyan] Exit"
        ]
        for item in menu_items:
            console.print(item)
        console.print()

    def handle_username_scan(self):
        self.show_section_title("USERNAME INTELLIGENCE")
        username = Prompt.ask("Enter target username").strip()
        if not username:
            console.print("[bold red]Username cannot be empty.[/bold red]")
            return
        self.show_platform_table()
        try:
            budget = int(Prompt.ask("Set scan budget (e.g 50 / 100 / 200 / 1000)"))
        except ValueError:
            console.print("[yellow]Invalid budget, using default 100[/yellow]")
            budget = 100
        platforms_input = Prompt.ask("Priority platforms (comma separated, optional)").strip()
        priority_platforms = [p.strip() for p in platforms_input.split(",") if p.strip()] if platforms_input else []
        self.logger.info(f"User scan -> {username} | budget={budget} | platforms={priority_platforms}")
        try:
            results = asyncio.run(
                self.scan_manager.execute_username_workflow(
                    username=username, budget=budget, priority_platforms=priority_platforms
                )
            )
            self.export_manager.export_and_display(
                results=results, title=f"Username Intelligence: {username}", username=username, category="username"
            )
            self.username_workflow.run(username, results)
            linked = next((r for r in results if r.platform == "Identity Correlation"), None)
            persona = next((r for r in results if r.platform == "Persona Classification"), None)
            if linked and linked.status == "FOUND":
                accounts = linked.extra.get("linked_accounts", [])
                if accounts:
                    console.print(f"\n[bold cyan]🔗 Linked Accounts Found:[/bold cyan] {len(accounts)}")
                    for acc in accounts[:5]:
                        console.print(f"   • {acc['platform_a']} ↔ {acc['platform_b']} (confidence: {acc['confidence']:.0%})")
                    if len(accounts) > 5:
                        console.print(f"   ... and {len(accounts) - 5} more")
            if persona and persona.status == "FOUND":
                p = persona.extra.get("persona", {})
                persona_name = p.get('persona', 'unknown').upper()
                persona_conf = p.get('confidence', 0)
                console.print(f"\n[bold magenta]👤 Digital Persona:[/bold magenta] {persona_name} (confidence: {persona_conf:.0%})")
                evidence = p.get("evidence", [])
                if evidence:
                    console.print(f"   Evidence: {', '.join(evidence[:5])}")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"Username workflow failed -> {exc}")

    def handle_email_scan(self):
        self.show_section_title("EMAIL INTELLIGENCE")
        email = Prompt.ask("Enter target email").strip()
        if not email:
            console.print("[bold red]Email cannot be empty.[/bold red]")
            return
        self.logger.info(f"Email scan -> {email}")
        try:
            with console.status(f"[bold green]Scanning email {email}...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_email_workflow(email))
            self.export_manager.export_and_display(
                results=results, title=f"Email Intelligence: {email}", username=email, category="email"
            )
            self.email_workflow.run(email, results)
            abstract = next((r for r in results if r.platform == "Abstract Email Reputation" and r.status == "FOUND"), None)
            if abstract:
                extra = abstract.extra
                lines = []
                if extra.get("deliverability_status"):
                    lines.append(f"[bold]Deliverability:[/bold] {extra['deliverability_status']}")
                if extra.get("deliverability_detail"):
                    lines.append(f"[bold]Detail:[/bold] {extra['deliverability_detail']}")
                if extra.get("quality_score") is not None:
                    lines.append(f"[bold]Quality Score:[/bold] {extra['quality_score']}")
                if extra.get("is_disposable"):
                    lines.append("[red]⚠ Disposable Email[/red]")
                if extra.get("address_risk_status"):
                    lines.append(f"[bold]Address Risk:[/bold] {extra['address_risk_status']}")
                if extra.get("domain_risk_status"):
                    lines.append(f"[bold]Domain Risk:[/bold] {extra['domain_risk_status']}")
                if extra.get("total_breaches"):
                    lines.append(f"[bold]Total Breaches (Abstract):[/bold] {extra['total_breaches']}")
                if extra.get("first_name") or extra.get("last_name"):
                    lines.append(f"[bold]Sender:[/bold] {extra.get('first_name','')} {extra.get('last_name','')}")
                if extra.get("organization"):
                    lines.append(f"[bold]Organization:[/bold] {extra['organization']}")
                if lines:
                    console.print(Panel("\n".join(lines), title="📧 Email Reputation Highlights", border_style="cyan"))
            gravatar = next((r for r in results if r.platform == "Gravatar" and r.status == "FOUND"), None)
            if gravatar:
                extra = gravatar.extra
                if extra.get("display_name") or extra.get("avatar_url"):
                    console.print(f"[cyan]🖼️ Gravatar Profile: {extra.get('display_name', 'N/A')} ({extra.get('avatar_url', '')})[/cyan]")
            mx = next((r for r in results if r.platform == "MX Check" and r.status == "FOUND"), None)
            if mx:
                console.print(f"[green]📬 MX Records Found: {', '.join(mx.extra.get('mx_servers', []))}[/green]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"Email workflow failed -> {exc}")

    def handle_domain_scan(self):
        self.show_section_title("DOMAIN INTELLIGENCE")
        domain = Prompt.ask("Enter target domain").strip()
        if not domain:
            console.print("[bold red]Domain cannot be empty.[/bold red]")
            return
        self.logger.info(f"Domain scan -> {domain}")
        try:
            with console.status(f"[bold green]Scanning domain {domain}...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_domain_workflow(domain))
            self.export_manager.export_and_display(
                results=results, title=f"Domain Intelligence: {domain}", username=domain, category="domain"
            )
            self.domain_workflow.run(domain, results)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"Domain workflow failed -> {exc}")

    def handle_phone_scan(self):
        self.show_section_title("PHONE INTELLIGENCE")
        phone = Prompt.ask("Enter phone number (international format, e.g., +62812345678)").strip()
        if not phone:
            console.print("[bold red]Phone number cannot be empty.[/bold red]")
            return
        self.logger.info(f"Phone scan -> {phone}")
        try:
            with console.status(f"[bold green]Scanning phone {phone}...", spinner="earth"):
                results = asyncio.run(self.phone_workflow.run(phone))
            self.export_manager.export_and_display(
                results=results, title=f"Phone Intelligence: {phone}", username=phone, category="phone"
            )
            abstract_phone = next((r for r in results if r.platform == "Abstract Phone Intel" and r.status == "FOUND"), None)
            if abstract_phone:
                extra = abstract_phone.extra
                lines = []
                if extra.get("carrier"):
                    lines.append(f"[bold]Carrier:[/bold] {extra['carrier']}")
                if extra.get("line_type"):
                    lines.append(f"[bold]Line Type:[/bold] {extra['line_type']}")
                if extra.get("risk_level"):
                    color = "red" if extra['risk_level'] == "high" else "yellow"
                    lines.append(f"[bold]Risk Level:[/bold] [{color}]{extra['risk_level'].upper()}[/{color}]")
                if extra.get("is_disposable"):
                    lines.append("[red]⚠ Disposable Number[/red]")
                if extra.get("total_breaches"):
                    lines.append(f"[bold]Total Breaches:[/bold] {extra['total_breaches']}")
                if lines:
                    console.print(Panel("\n".join(lines), title="📱 Phone Intel Highlights", border_style="cyan"))
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"Phone workflow failed -> {exc}")

    def handle_image_scan(self):
        self.show_section_title("IMAGE INTELLIGENCE")
        image_path = Prompt.ask("Enter image path (local file or URL)").strip()
        if not image_path:
            console.print("[bold red]Path cannot be empty.[/bold red]")
            return
        self.logger.info(f"Image scan -> {image_path}")
        try:
            with Progress(
                SpinnerColumn(), TextColumn("[cyan]Analyzing image...[/cyan]"),
                BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("scan", total=100)
                async def run_workflow():
                    loop = asyncio.get_running_loop()
                    scan_results, raw = await self.scan_manager.image_scanner.scan_image(image_path)
                    progress.update(task, advance=100)
                    return scan_results, raw
                results, raw = asyncio.run(run_workflow())
            if raw:
                self.scan_manager.image_scanner.workflow.display_terminal_report(raw)
            if results:
                self.scan_manager.storage.save_scan(image_path, results)
            if raw:
                safe_name = self.scan_manager.image_scanner._sanitize_name(os.path.basename(image_path))
                self.scan_manager.image_scanner.workflow.export_results(raw, safe_name)
            console.print("[green]Image intelligence scan completed successfully.[/green]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"Image workflow failed -> {exc}")

    def handle_ai_analysis(self):
        self.show_section_title("AI ANALYSIS")
        console.print("[bold]Module:[/bold]")
        console.print("[1] Username")
        console.print("[2] Email")
        console.print("[3] Domain")
        console.print("[4] Phone")
        console.print("[5] Image")
        console.print("[6] Video")
        console.print("[0] Back")
        choice = Prompt.ask("Choose module").strip()
        module_map = {"1": "username", "2": "email", "3": "domain", "4": "phone", "5": "image", "6": "video"}
        module_name = module_map.get(choice)
        if not module_name:
            return
        target = Prompt.ask("Enter target identifier (username/email/domain/phone/image/video path)").strip()
        if not target:
            console.print("[red]Target required[/red]")
            return
        snapshot = self.scan_manager.storage.get_latest_scan(target)
        if not snapshot:
            console.print(f"[yellow]No scan history for '{target}'[/yellow]")
            return
        self.logger.info(f"AI Analysis -> {target} ({module_name})")
        try:
            if module_name == "video":
                from core.video.ai.ai_video_analyzer import AIVideoAnalyzer
                ai_video = AIVideoAnalyzer()
                result_scan = ai_video.analyze(snapshot, file_path=target)
                analysis = result_scan.extra
                console.print(f"\n[bold cyan]AI Analysis Report for {target}[/bold cyan]")
                console.print(f"Risk Level: [bold]{analysis.get('threat_level', 'unknown').upper()}[/bold]")
                console.print(f"Risk Score: {analysis.get('threat_score', 0)}/100")
                console.print(f"Confidence: {analysis.get('confidence_score', 0)}%")
                console.print(f"\nSummary: {analysis.get('executive_summary', 'N/A')}")
                console.print(f"\nLocation Hypothesis: {analysis.get('location_hypothesis', 'N/A')}")
                console.print(f"Threat Analysis: {analysis.get('threat_analysis', 'N/A')}")
                console.print(f"Recommended Steps: {', '.join(analysis.get('recommended_steps', []))}")
                return
            with console.status("[bold green]Gemini is analyzing...[/bold green]", spinner="earth"):
                result = asyncio.run(self.ai_workflow.execute(target, module_name, snapshot))
            analysis = result["ai_analysis"]
            console.print(f"\n[bold cyan]AI Analysis Report for {target}[/bold cyan]")
            console.print(f"Risk Level: [bold]{analysis.get('risk_level', 'unknown').upper()}[/bold]")
            console.print(f"Risk Score: {analysis.get('risk_score', 0)}/100")
            console.print(f"Confidence: {analysis.get('confidence_estimate', 0)}%")
            console.print(f"\nSummary: {analysis.get('summary', 'N/A')}")
            console.print(f"\nCorrelations: {', '.join(analysis.get('correlations', []))}")
            console.print(f"Suspicious: {', '.join(analysis.get('suspicious_findings', []))}")
            console.print(f"Insights: {', '.join(analysis.get('insights', []))}")
            console.print(f"\n[green]Full report saved to results/ai/{target}/[/green]")
        except Exception as exc:
            console.print(f"[red]AI analysis failed: {exc}[/red]")
            self.logger.error(f"AI workflow error: {exc}")

    def handle_graph_menu(self):
        self.show_section_title("RELATIONSHIP GRAPH")
        console.print("[1] Build graph from all data")
        console.print("[2] Build graph for specific identifier")
        console.print("[3] Show centrality")
        console.print("[4] Show connected components")
        console.print("[5] Export graph (GEXF/JSON)")
        console.print("[6] Delta graph (compare two snapshots)")
        console.print("[0] Back")
        choice = Prompt.ask("Choose").strip()
        if choice == "1":
            graph = self.graph_builder.build_graph()
            self.graph_visualizer = GraphVisualizer(graph)
            nodes = graph.number_of_nodes()
            edges = graph.number_of_edges()
            console.print(f"[green]✅ Graph built with {nodes} nodes and {edges} edges[/green]")
            if nodes > 0:
                self._show_graph_summary(graph)
        elif choice == "2":
            identifier = Prompt.ask("Enter username/email/domain/phone to focus")
            graph = self.graph_builder.build_graph(username_filter=identifier)
            self.graph_visualizer = GraphVisualizer(graph)
            nodes = graph.number_of_nodes()
            edges = graph.number_of_edges()
            console.print(f"[green]✅ Graph built with {nodes} nodes and {edges} edges[/green]")
            if nodes > 0:
                self._show_graph_summary(graph)
        elif choice == "3":
            if not self.graph_visualizer:
                console.print("[red]Graph belum dibangun. Pilih 1/2 dulu.[/red]")
            else:
                self.graph_visualizer.show_centrality_table()
        elif choice == "4":
            if not self.graph_visualizer:
                console.print("[red]Graph belum dibangun.[/red]")
            else:
                self.graph_visualizer.show_components_summary()
        elif choice == "5":
            if not self.graph_visualizer:
                console.print("[red]Graph belum dibangun.[/red]")
                return
            fmt = Prompt.ask("Export format (gexf/json)", default="gexf")
            filename = Prompt.ask("Output path", default="results/graph/identity_graph")
            os.makedirs("results/graph", exist_ok=True)
            if fmt == "gexf":
                path = self.graph_visualizer.export_gexf(f"{filename}.gexf")
            else:
                path = self.graph_visualizer.export_json(f"{filename}.json")
            console.print(f"[green]Graph exported to {path}[/green]")
        elif choice == "6":
            identifier = Prompt.ask("Enter identifier")
            timestamps = self.scan_manager.storage.get_distinct_timestamps(identifier)
            if len(timestamps) < 2:
                console.print("[red]Need at least 2 scans[/red]")
                return
            self._show_timestamp_selection(identifier, timestamps)
            try:
                idx1 = int(Prompt.ask("Older scan number")) - 1
                idx2 = int(Prompt.ask("Newer scan number")) - 1
                if idx1 < 0 or idx1 >= len(timestamps) or idx2 < 0 or idx2 >= len(timestamps):
                    console.print("[red]Invalid index[/red]")
                    return
                ts1 = timestamps[idx1]
                ts2 = timestamps[idx2]
                delta = self.delta_graph.compare_timestamps(identifier, ts1, ts2)
                self._display_delta_graph(delta)
            except ValueError:
                console.print("[red]Invalid input[/red]")

    def _show_graph_summary(self, graph):
        from core.graph.graph_builder import GraphBuilder
        builder = GraphBuilder(None)
        builder.graph = graph
        top = builder.get_centrality(3)
        if top:
            console.print("\n[bold]🔝 Top 3 Most Connected:[/bold]")
            for i, (node, score) in enumerate(top, 1):
                console.print(f"  {i}. {node} (centrality: {score:.3f})")
        comps = builder.get_connected_components()
        if comps:
            largest = max(comps, key=len)
            console.print(f"\n[bold]🧩 Largest component:[/bold] {len(largest)} nodes")
            console.print(f"   {', '.join(sorted(largest)[:5])}{'...' if len(largest)>5 else ''}")

    def _show_timestamp_selection(self, identifier, timestamps):
        table = Table(title=f"Available snapshots for {identifier}")
        table.add_column("No", style="cyan")
        table.add_column("Timestamp", style="white")
        for i, ts in enumerate(timestamps, 1):
            table.add_row(str(i), ts)
        console.print(table)

    def _display_delta_graph(self, delta: dict):
        table = Table(title="Delta Graph Changes", border_style="bright_magenta")
        table.add_column("Type", style="bold")
        table.add_column("Count", style="cyan")
        table.add_column("Details", style="white")
        table.add_row("[green]New Nodes[/green]", str(len(delta["new_nodes"])), ", ".join(delta["new_nodes"][:5]))
        table.add_row("[red]Removed Nodes[/red]", str(len(delta["removed_nodes"])), ", ".join(delta["removed_nodes"][:5]))
        table.add_row("[green]New Edges[/green]", str(len(delta["new_edges"])), str(delta["new_edges"][:3]))
        table.add_row("[red]Removed Edges[/red]", str(len(delta["removed_edges"])), str(delta["removed_edges"][:3]))
        console.print(table)

    def handle_history_menu(self):
        self.show_section_title("SCAN HISTORY & DELTA")
        cur = self.scan_manager.storage.execute(
            "SELECT DISTINCT username FROM scan_results ORDER BY username"
        )
        targets = [row["username"] for row in cur.fetchall()]
        if not targets:
            console.print("[yellow]Belum ada data history sama sekali.[/yellow]")
            return
        table = Table(title="Available Targets", border_style="cyan")
        table.add_column("No", style="cyan", justify="right")
        table.add_column("Target", style="white")
        table.add_column("Type", style="green")
        for i, t in enumerate(targets, 1):
            module = self._guess_module_from_target(t)
            table.add_row(str(i), t, module)
        table.add_row("0", "[italic]Enter manually[/italic]", "")
        console.print(table)
        choice = Prompt.ask("Choose target number (or 0 to type)", default="0").strip()
        if choice == "0":
            identifier = Prompt.ask("Enter target (username/email/domain/phone)").strip()
        else:
            try:
                idx = int(choice) - 1
                identifier = targets[idx]
            except (ValueError, IndexError):
                console.print("[red]Invalid choice[/red]")
                return
        if not identifier:
            return
        timestamps = self.scan_manager.storage.get_distinct_timestamps(identifier)
        if not timestamps:
            console.print(f"[yellow]No scan history for '{identifier}'[/yellow]")
            return
        table = Table(title=f"Scan History for {identifier}")
        table.add_column("No", style="cyan")
        table.add_column("Timestamp", style="white")
        table.add_column("Results", style="green")
        for i, ts in enumerate(timestamps, 1):
            snapshot = self.scan_manager.storage.get_scan_snapshot(identifier, ts)
            found = sum(1 for r in snapshot if r.status == "FOUND")
            total = len(snapshot)
            table.add_row(str(i), ts, f"{found}/{total} found")
        console.print(table)
        console.print("\n[bold]Options:[/bold]")
        console.print("[1] Compare two scans")
        console.print("[2] Quick delta (latest vs previous)")
        console.print("[3] View a scan detail")
        console.print("[0] Back")
        choice = Prompt.ask("Choose").strip()
        if choice == "1":
            if len(timestamps) < 2:
                console.print("[red]Need at least 2 scans[/red]")
                return
            try:
                idx1 = int(Prompt.ask("Older scan number")) - 1
                idx2 = int(Prompt.ask("Newer scan number")) - 1
                if idx1 < 0 or idx1 >= len(timestamps) or idx2 < 0 or idx2 >= len(timestamps):
                    console.print("[red]Invalid index[/red]")
                    return
                ts1 = timestamps[idx1]
                ts2 = timestamps[idx2]
                self._show_and_export_delta(identifier, ts1, ts2)
            except ValueError:
                console.print("[red]Invalid input[/red]")
        elif choice == "2":
            if len(timestamps) >= 2:
                ts_prev = timestamps[1]
                ts_latest = timestamps[0]
                self._show_and_export_delta(identifier, ts_prev, ts_latest)
            else:
                console.print("[yellow]Only one scan, no comparison possible[/yellow]")
        elif choice == "3":
            try:
                idx = int(Prompt.ask("Scan number")) - 1
                if idx < 0 or idx >= len(timestamps):
                    console.print("[red]Invalid index[/red]")
                    return
                ts = timestamps[idx]
                snapshot = self.scan_manager.storage.get_scan_snapshot(identifier, ts)
                self.export_manager.formatter.display_full_report(
                    snapshot, f"Snapshot {ts}", username=identifier, export=False
                )
            except ValueError:
                console.print("[red]Invalid input[/red]")

    def _guess_module_from_target(self, target: str) -> str:
        if "@" in target:
            return "email"
        if target.startswith("+"):
            return "phone"
        if "\\" in target or (target.startswith("http") and "://" in target):
            return "image"
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
            return "ip"
        video_exts = (".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v")
        if target.lower().endswith(video_exts):
            return "video"
        if "." in target and not target.startswith("C:"):
            return "domain"
        return "username"

    def _show_and_export_delta(self, username, ts1, ts2):
        delta = self.scan_manager.storage.compare_scans(username, ts1, ts2)
        self._display_delta_table(delta)
        if delta["changes"] and Prompt.ask("Export delta to CSV?", default="y").lower() == "y":
            out_dir = Path("Osint") / "results" / "delta" / username
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"delta_{ts1[:10]}_{ts2[:10]}.csv"
            self.scan_manager.storage.export_delta_csv(username, ts1, ts2, str(out_path))
            console.print(f"[green]Delta exported to {out_path}[/green]")

    def _display_delta_table(self, delta: dict):
        if not delta["changes"]:
            console.print("[yellow]No changes detected[/yellow]")
            return
        table = Table(title="Delta Detection Results", border_style="bright_magenta")
        table.add_column("Type", style="bold")
        table.add_column("Platform")
        table.add_column("Details")
        for ch in delta["changes"]:
            color = {"NEW": "green", "LOST": "red", "UPDATED": "yellow"}.get(ch["type"], "white")
            table.add_row(f"[{color}]{ch['type']}[/{color}]", ch["platform"], ch["details"])
        console.print(table)

    def handle_report_generator(self):
        self.show_section_title("PDF REPORT GENERATOR")
        target = Prompt.ask("Enter target identifier (username/email/domain/phone/image/video path)").strip()
        if not target:
            console.print("[red]Target required[/red]")
            return
        module_name = self._guess_module_from_target(target)

        if module_name == "video":
            snapshot = self.scan_manager.storage.get_latest_scan(target)
            if not snapshot:
                console.print(f"[yellow]No scan history for '{target}'. Run Video Intelligence first.[/yellow]")
                return
            ai_dir = Path("Osint") / "results" / "ai" / re.sub(r'[<>:"/\\|?*]', '_', target)
            ai_exists = (ai_dir / "ai_analysis.json").exists()
            if not ai_exists:
                console.print("[yellow]AI Analysis belum tersedia untuk video ini.[/yellow]")
                if Prompt.ask("Jalankan AI Analysis terlebih dahulu?", choices=["y", "n"], default="y") == "y":
                    try:
                        with console.status("[bold green]Gemini is analyzing...[/bold green]", spinner="earth"):
                            from core.video.ai.ai_video_analyzer import AIVideoAnalyzer
                            ai_video = AIVideoAnalyzer()
                            result = ai_video.analyze(snapshot, file_path=target)
                            ai_dir.mkdir(parents=True, exist_ok=True)
                            with open(ai_dir / "ai_analysis.json", "w", encoding="utf-8") as f:
                                json.dump(result.extra, f, indent=2, ensure_ascii=False)
                        console.print("[green]AI Analysis selesai.[/green]")
                    except Exception as exc:
                        console.print(f"[red]AI Analysis gagal: {exc}[/red]")
                        return
                else:
                    console.print("[yellow]Lanjut membuat laporan tanpa AI Analysis.[/yellow]")
            self.logger.info(f"Generating report for video: {target}")
            try:
                with console.status("[bold green]Generating report...[/bold green]", spinner="earth"):
                    output = self.report_generator.generate_video_report(target, snapshot)
                console.print(f"[green]Report saved to {output}[/green]")
                if (output / "osint_report.html").exists():
                    console.print(f"[green]HTML: {output / 'osint_report.html'}[/green]")
                if (output / "osint_report.pdf").exists():
                    console.print(f"[green]PDF: {output / 'osint_report.pdf'}[/green]")
                else:
                    console.print("[yellow]PDF tidak dibuat. Pastikan WeasyPrint terinstal.[/yellow]")
                return
            except Exception as exc:
                console.print(f"[red]Report generation failed: {exc}[/red]")
                return

        # Untuk modul selain video
        ai_dir = Path("Osint") / "results" / "ai" / self.report_generator.collector._sanitize_target(target)
        ai_exists = (ai_dir / "ai_analysis.json").exists()
        if not ai_exists:
            console.print("[yellow]AI Analysis belum tersedia untuk target ini.[/yellow]")
            if Prompt.ask("Jalankan AI Analysis terlebih dahulu?", choices=["y", "n"], default="y") == "y":
                snapshot = self.scan_manager.storage.get_latest_scan(target)
                if snapshot:
                    m = self._guess_module_from_scan(snapshot)
                else:
                    m = "username"
                try:
                    with console.status("[bold green]Gemini is analyzing...[/bold green]", spinner="earth"):
                        asyncio.run(self.ai_workflow.execute(target, m, snapshot or []))
                    console.print("[green]AI Analysis selesai.[/green]")
                except Exception as exc:
                    console.print(f"[red]AI Analysis gagal: {exc}[/red]")
                    return
            else:
                console.print("[yellow]Lanjut membuat laporan tanpa AI Analysis.[/yellow]")
        self.logger.info(f"Generating PDF report for {target}")
        try:
            with console.status("[bold green]Generating PDF report...[/bold green]", spinner="earth"):
                output = self.report_generator.generate(target)
            console.print(f"[green]Report saved to {output}[/green]")
            html_path = output / "osint_report.html"
            pdf_path = output / "osint_report.pdf"
            if html_path.exists():
                console.print(f"[green]HTML: {html_path}[/green]")
            if pdf_path.exists():
                console.print(f"[green]PDF: {pdf_path}[/green]")
            else:
                console.print("[yellow]PDF tidak dibuat. Pastikan WeasyPrint atau wkhtmltopdf terinstal.[/yellow]")
        except Exception as exc:
            console.print(f"[red]Report generation failed: {exc}[/red]")
            self.logger.error(f"Report error: {exc}")

    def _guess_module_from_scan(self, snapshot) -> str:
        if not snapshot:
            return "username"
        platform = snapshot[0].platform.lower()
        if any(w in platform for w in ["instagram","github","twitter","tiktok","reddit","linkedin"]):
            return "username"
        if any(w in platform for w in ["haveibeenpwned","gravatar","emailrep","hunter"]):
            return "email"
        if any(w in platform for w in ["whois","dns","ssl","subdomain"]):
            return "domain"
        if any(w in platform for w in ["phone","numverify","whatsapp","telegram"]):
            return "phone"
        if any(w in platform for w in ["exif","ocr","face","steganography"]):
            return "image"
        if any(w in platform for w in ["video","metadata","frame"]):
            return "video"
        return "username"

    def handle_ip_scan(self):
        self.show_section_title("IP INTELLIGENCE")
        ip_address = Prompt.ask("Enter IP address (e.g., 8.8.8.8)").strip()
        if not ip_address:
            console.print("[bold red]IP address cannot be empty.[/bold red]")
            return
        self.logger.info(f"IP scan -> {ip_address}")
        try:
            with console.status(f"[bold green]Scanning IP {ip_address}...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_ip_workflow(ip_address))
            self.export_manager.export_and_display(
                results=results, title=f"IP Intelligence: {ip_address}", username=ip_address, category="ip"
            )
            self.ip_workflow.run(ip_address, results)
            geo = next((r for r in results if r.platform == "Geolocation" and r.status == "FOUND"), None)
            rdns = next((r for r in results if r.platform == "Reverse DNS" and r.status == "FOUND"), None)
            rep = next((r for r in results if r.platform == "Reputation" and r.status == "FOUND"), None)
            infra = next((r for r in results if r.platform == "Infrastructure Analysis" and r.status == "FOUND"), None)
            lines = []
            if geo:
                e = geo.extra
                if e.get("source"):
                    lines.append(f"[bold]📡 Source:[/bold] {e['source']}")
                if e.get("city") or e.get("country"):
                    loc = ", ".join(filter(None, [e.get("city"), e.get("region"), e.get("country")]))
                    flag = e.get("flag_emoji", "")
                    lines.append(f"[bold]📍 Location:[/bold] {loc} {flag}")
                lat, lon = e.get("latitude"), e.get("longitude")
                if lat is not None and lon is not None:
                    lines.append(f"[bold]🗺️  Coordinates:[/bold] {lat}, {lon}")
                if e.get("asn"):
                    lines.append(f"[bold]🔢 ASN:[/bold] AS{e['asn']} ({e.get('asn_name', 'Unknown')})")
                isp = e.get("isp") or e.get("asn_name") or e.get("company_name")
                if isp:
                    lines.append(f"[bold]🏢 ISP/Org:[/bold] {isp}")
                tz = e.get("timezone_name")
                local = e.get("local_time")
                if tz:
                    lines.append(f"[bold]🕒 Timezone:[/bold] {tz}" + (f" ({local})" if local else ""))
                currency = e.get("currency_symbol") or e.get("currency_code")
                if currency:
                    lines.append(f"[bold]💱 Currency:[/bold] {currency}")
                sec_flags = []
                for key, label in [("is_vpn", "VPN"), ("is_proxy", "Proxy"), ("is_tor", "TOR"),
                                   ("is_hosting", "Hosting"), ("is_relay", "Relay"),
                                   ("is_mobile", "Mobile"), ("is_abuse", "Abusive")]:
                    if e.get(key):
                        sec_flags.append(f"[red]{label}[/red]" if key != "is_mobile" else f"[green]{label}[/green]")
                if sec_flags:
                    lines.append(f"[bold]🔒 Security:[/bold] " + " ".join(sec_flags))
            if rdns:
                hosts = rdns.extra.get("reverse_dns", [])
                if hosts:
                    lines.append(f"[bold]🔄 Reverse DNS:[/bold] {', '.join(hosts[:3])}")
            if rep:
                abuse_score = rep.extra.get("abuse_score", 0)
                total_reports = rep.extra.get("total_reports", 0)
                if abuse_score > 0:
                    color = "red" if abuse_score > 80 else "yellow" if abuse_score > 40 else "green"
                    lines.append(f"[bold]⚠️ Abuse Score:[/bold] [{color}]{abuse_score}%[/{color}] ({total_reports} reports)")
            if infra:
                if infra.extra.get("cloud_provider"):
                    lines.append(f"[bold]☁️ Cloud Provider:[/bold] {infra.extra['cloud_provider']}")
                if infra.extra.get("hosting_provider"):
                    lines.append(f"[bold]🏗️ Hosting Provider:[/bold] {infra.extra['hosting_provider']}")
                if infra.extra.get("infrastructure_type"):
                    lines.append(f"[bold]🏷️ Infrastructure Type:[/bold] {infra.extra['infrastructure_type']}")
            if lines:
                console.print(Panel("\n".join(lines), title="🌍 IP Intelligence Full Report", border_style="cyan"))
            else:
                console.print("[yellow]Tidak ada data tambahan untuk IP ini.[/yellow]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print("\n[bold red]Unexpected error occurred.[/bold red]")
            self.logger.error(f"IP workflow failed -> {exc}")

    def handle_company_scan(self):
        self.show_section_title("COMPANY INTELLIGENCE")
        domain = Prompt.ask("Enter company domain (e.g., airbnb.com)").strip()
        if not domain:
            console.print("[bold red]Domain cannot be empty.[/bold red]")
            return
        self.logger.info(f"Company scan -> {domain}")
        try:
            with console.status(f"[bold green]Scanning company {domain}...", spinner="earth"):
                scan_results, full_report = asyncio.run(
                    self.scan_manager.execute_company_workflow(domain)
                )
            self.export_manager.export_and_display(
                results=scan_results, title=f"Company Intelligence: {domain}", username=domain, category="company"
            )
            self.company_workflow.run(domain, scan_results)
            lines = []
            api = full_report.get("company_api", {})
            if api:
                if api.get("company_name"):
                    lines.append(f"[bold]🏢 Company:[/bold] {api['company_name']}")
                if api.get("industry"):
                    lines.append(f"[bold]🏭 Industry:[/bold] {api['industry']}")
                if api.get("employee_range"):
                    lines.append(f"[bold]👥 Employees:[/bold] {api['employee_range']}")
                if api.get("revenue_range"):
                    lines.append(f"[bold]💰 Revenue:[/bold] {api['revenue_range']}")
                if api.get("city") and api.get("country"):
                    lines.append(f"[bold]📍 HQ:[/bold] {api['city']}, {api['country']}")
                if api.get("ticker"):
                    lines.append(f"[bold]📈 Ticker:[/bold] {api['ticker']} ({api.get('exchange', '')})")
                if api.get("linkedin_url"):
                    lines.append(f"[bold]🔗 LinkedIn:[/bold] {api['linkedin_url']}")
            whois = full_report.get("whois", {})
            if whois.get("status") == "FOUND":
                lines.append(f"[bold]🔍 WHOIS:[/bold] Registrar: {whois.get('registrar', 'N/A')}")
                if whois.get("creation_date"):
                    lines.append(f"[bold]📅 Domain Created:[/bold] {whois['creation_date']}")
                if whois.get("expiration_date"):
                    lines.append(f"[bold]⏳ Domain Expires:[/bold] {whois['expiration_date']}")
            dns = full_report.get("dns", {})
            if dns:
                if dns.get("provider_identified"):
                    lines.append(f"[bold]🌐 DNS Provider:[/bold] {dns['provider_identified']}")
                cdn = dns.get("cdn_detected", [])
                if cdn:
                    lines.append(f"[bold]⚡ CDN:[/bold] {', '.join(cdn)}")
                email_sec = dns.get("email_security", {})
                lines.append(f"[bold]📧 Email Security:[/bold] SPF {'✅' if email_sec.get('spf') else '❌'}  DMARC {'✅' if email_sec.get('dmarc') else '❌'}  DKIM {'✅' if email_sec.get('dkim') else '❌'}")
                if dns.get("suspicious_txt"):
                    lines.append(f"[bold]⚠️ Suspicious TXT Records:[/bold] {len(dns['suspicious_txt'])} ditemukan")
                if dns.get("dangling_cname"):
                    lines.append(f"[bold]⚠️ Dangling CNAME:[/bold] {len(dns['dangling_cname'])} ditemukan")
            sub = full_report.get("subdomains", {})
            if sub:
                count = sub.get("count", 0)
                lines.append(f"[bold]🔗 Subdomains:[/bold] {count} ditemukan")
                if count > 0:
                    classification = sub.get("classification", {})
                    if classification:
                        class_str = ", ".join(f"{k}: {v}" for k, v in classification.items() if v)
                        if class_str:
                            lines.append(f"[bold]   📊 Classification:[/bold] {class_str}")
            tech = full_report.get("technologies", {})
            if tech.get("technologies"):
                lines.append(f"[bold]💻 Technologies:[/bold] {', '.join(tech['technologies'][:15])}")
            saas = full_report.get("saas_detected", {})
            if saas:
                saas_list = []
                for k, v in saas.items():
                    if isinstance(v, list):
                        saas_list.append(k)
                    else:
                        saas_list.append(f"{k} ({v})")
                lines.append(f"[bold]☁️ SaaS Detected:[/bold] {', '.join(saas_list[:10])}")
            exp = full_report.get("exposure", {})
            if exp.get("findings"):
                sev = exp.get("severity_summary", {})
                sev_str = ", ".join(f"{k}: {v}" for k, v in sev.items() if v > 0)
                lines.append(f"[bold]🚨 Exposure Findings:[/bold] {len(exp['findings'])} ({sev_str})")
                critical_high = [f for f in exp["findings"] if f.get("severity") in ("CRITICAL", "HIGH")]
                for f in critical_high[:5]:
                    lines.append(f"[bold]   {f.get('severity', '')}[/bold]: {f.get('path', '')} - {f.get('message', '')}")
            risk = full_report.get("risk_assessment", {})
            if risk:
                threat_level = risk.get("threat_level", "UNKNOWN")
                color = "red" if threat_level in ("CRITICAL", "HIGH") else "yellow" if threat_level == "MEDIUM" else "green"
                lines.append(f"[bold]⚠️ Risk Level:[/bold] [{color}]{threat_level}[/{color}] (Score: {risk.get('total_risk_score', 0)}/100)")
                cat_scores = risk.get("category_scores", {})
                if cat_scores:
                    cat_str = ", ".join(f"{k.replace('_risk','')}: {v:.0f}" for k, v in cat_scores.items())
                    lines.append(f"[bold]   📊 Categories:[/bold] {cat_str}")
            corr = full_report.get("correlation", {})
            if corr:
                findings = corr.get("correlation_findings", [])
                if findings:
                    lines.append(f"[bold]🔗 Correlations:[/bold] {len(findings)} ditemukan")
                    for f in findings[:3]:
                        lines.append(f"   • {f}")
            if lines:
                console.print(Panel("\n".join(lines), title="🏢 Company Intelligence Full Report", border_style="cyan"))
            else:
                console.print("[yellow]Data perusahaan tidak cukup untuk ditampilkan.[/yellow]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print(f"\n[bold red]Unexpected error occurred: {exc}[/bold red]")
            self.logger.error(f"Company workflow failed -> {exc}")

    def handle_correlation(self):
        self.show_section_title("CROSS‑MODULE CORRELATION")
        console.print("[bold]Analyzing all modules for identity relationships...[/bold]")
        try:
            with console.status("[bold green]Correlating entities...[/bold green]", spinner="earth"):
                result = self.scan_manager.correlation_workflow.execute_all()
            if "error" in result:
                console.print(f"[red]{result['error']}[/red]")
                return
            console.print(f"\n[bold cyan]Correlation Complete![/bold cyan]")
            console.print(f"Relationships Found: {result['total_relationships']}")
            console.print(f"Identity Clusters: {result['total_clusters']}")
            console.print(f"Graph Nodes: {result['graph_nodes']} | Edges: {result['graph_edges']}")
            console.print(f"\n[green]Reports saved to {result['output_directory']}[/green]")
            if result.get("clusters"):
                console.print("\n[bold]Top Identity Clusters:[/bold]")
                for i, cluster in enumerate(result["clusters"][:5], 1):
                    console.print(f"  {i}. {', '.join(cluster['members'][:5])} (confidence: {cluster['average_confidence']:.2f})")
        except Exception as exc:
            console.print(f"[red]Correlation failed: {exc}[/red]")

    def handle_document_scan(self):
        self.show_section_title("DOCUMENT INTELLIGENCE")
        file_path = Prompt.ask("Enter document file path").strip()
        if not file_path:
            console.print("[bold red]Path cannot be empty.[/bold red]")
            return
        self.logger.info(f"Document scan -> {file_path}")
        try:
            with console.status(f"[bold green]Scanning document...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_document_workflow(file_path))
            self.export_manager.export_and_display(
                results=results, title=f"Document Intelligence: {os.path.basename(file_path)}",
                username=file_path, category="document"
            )
            self.document_workflow.run(file_path, results)
            for r in results:
                if r.platform == "Sensitive Data Detection" and r.status == "FOUND":
                    s = r.extra
                    lines = []
                    if s.get("emails"):
                        lines.append(f"📧 Emails: {', '.join(s['emails'][:5])}")
                    if s.get("phones"):
                        lines.append(f"📞 Phones: {', '.join(s['phones'][:5])}")
                    if s.get("api_keys"):
                        lines.append(f"🔑 API Keys Found: {len(s['api_keys'])}")
                    if s.get("tokens"):
                        lines.append(f"🎟️ Tokens Found: {len(s['tokens'])}")
                    if lines:
                        console.print(Panel("\n".join(lines), title="🔍 Sensitive Data Found", border_style="cyan"))
                    break
        except Exception as exc:
            console.print(f"[red]Document scan failed: {exc}[/red]")
            self.logger.error(f"Document workflow error: {exc}")

    def handle_darkweb_scan(self):
        self.show_section_title("DARK WEB INTELLIGENCE")
        target = Prompt.ask("Enter email, username, domain, phone, or IP").strip()
        if not target:
            console.print("[bold red]Target cannot be empty.[/bold red]")
            return
        self.logger.info(f"Dark web scan -> {target}")
        try:
            with console.status("[bold green]Scanning dark web...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_darkweb_workflow(target))
            self.export_manager.export_and_display(
                results=results, title=f"Dark Web Intelligence: {target}", username=target, category="darkweb"
            )
            self.darkweb_workflow.run(target, results)
            for r in results:
                if r.platform == "Breach Analysis" and r.status == "FOUND":
                    b = r.extra
                    console.print(f"\n[bold red]🔥 Breaches Found:[/bold red] {b.get('total_breaches', 0)}")
                    if b.get("plaintext_password_exposure"):
                        console.print("[bold red]⚠️ PLAINTEXT PASSWORD EXPOSURE DETECTED[/bold red]")
                if r.platform == "Risk Assessment" and r.status == "FOUND":
                    risk = r.extra
                    level = risk.get("risk_level", "UNKNOWN")
                    color = "red" if level in ("CRITICAL", "HIGH") else "yellow" if level == "MEDIUM" else "green"
                    console.print(f"[bold]Risk Level:[/bold] [{color}]{level}[/{color}] (Score: {risk.get('risk_score', 0)}/100)")
        except Exception as exc:
            console.print(f"[red]Dark web scan failed: {exc}[/red]")
            self.logger.error(f"Dark web workflow error: {exc}")

    def handle_video_scan(self):
        self.show_section_title("VIDEO INTELLIGENCE")
        file_path = Prompt.ask("Enter video file path").strip()
        if not file_path:
            console.print("[bold red]Path cannot be empty.[/bold red]")
            return
        self.logger.info(f"Video scan -> {file_path}")
        try:
            with console.status("[bold green]Scanning video...", spinner="earth"):
                results = asyncio.run(self.scan_manager.execute_video_workflow(file_path))
            self.export_manager.export_and_display(
                results=results, title=f"Video Intelligence: {os.path.basename(file_path)}",
                username=file_path, category="video"
            )
            self.video_workflow.run(file_path, results)
            for r in results:
                if r.platform == "Video Metadata" and r.status == "FOUND":
                    v = r.extra.get("video", {})
                    if v:
                        console.print(f"\n[bold cyan]📹 Resolution:[/bold cyan] {v.get('resolution', 'N/A')} | Duration: {round(r.extra.get('duration_seconds', 0), 1)}s")
                if r.platform == "Face Detection" and r.status == "FOUND":
                    console.print(f"[bold cyan]👤 Faces Found:[/bold cyan] {r.extra.get('total_faces', 0)}")
                if r.platform == "OCR Analysis" and r.status == "FOUND":
                    e = r.extra
                    if e.get("emails"):
                        console.print(f"[bold cyan]📧 Emails:[/bold cyan] {', '.join(e['emails'][:5])}")
                    if e.get("phones"):
                        console.print(f"[bold cyan]📞 Phones:[/bold cyan] {', '.join(e['phones'][:5])}")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        except Exception as exc:
            console.print(f"[red]Video scan failed: {exc}[/red]")
            self.logger.error(f"Video workflow error: {exc}")

    def handle_menu_choice(self, choice: str):
        routes = {
            "1": self.handle_username_scan, "2": self.handle_email_scan, "3": self.handle_domain_scan,
            "4": self.handle_phone_scan, "5": self.handle_image_scan, "6": self.handle_ai_analysis,
            "7": self.handle_graph_menu, "8": self.handle_history_menu, "9": self.handle_report_generator,
            "10": self.handle_ip_scan, "11": self.handle_company_scan, "12": self.handle_correlation,
            "13": self.handle_document_scan, "14": self.handle_darkweb_scan, "15": self.handle_video_scan,
            "0": self.shutdown,
        }
        action = routes.get(choice)
        if action:
            action()
        else:
            console.print("[bold red]Invalid menu choice[/bold red]")

    def run(self):
        self.initialize()
        while self.running:
            try:
                self.banner.show_startup_screen()
                self.show_main_menu()
                choice = Prompt.ask("Select menu").strip()
                self.handle_menu_choice(choice)
            except KeyboardInterrupt:
                self.shutdown()
            if self.running:
                self.pause()

    def shutdown(self):
        console.print("\n[bold red]Shutting down OSINT Fusion...[/bold red]")
        self.logger.info("Application shutdown initiated")
        self.running = False
        self.logger.success("OSINT Fusion shutdown complete")
        self.logger.divider()


if __name__ == "__main__":
    app = OSINTFusionApp()
    app.run()