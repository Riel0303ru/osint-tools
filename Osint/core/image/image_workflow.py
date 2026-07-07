# core/image/image_workflow.py
from __future__ import annotations

import os
import json
import csv
from typing import List, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from core.image.exif_engine import EXIFEngine
from core.image.ocr_engine import OCREngine
from core.image.face_detector import FaceDetector
from core.image.perceptual_hash import PerceptualHash
from core.image.stego_check import StegoCheck
from core.image.reverse_search import ReverseSearch
from core.image.object_detector import ObjectDetector
from core.image.image_intelligence import ImageIntelligence
from core.base.scan_result import ScanResult

console = Console()


class ImageWorkflow:
    """Orchestrates full image intelligence pipeline."""

    def __init__(self, base_dir: str = "Osint"):
        """
        Args:
            base_dir: Root folder untuk output (default "Osint").
                      Hasil scan akan disimpan di <base_dir>/results/image/<target>/
        """
        self.exif_engine = EXIFEngine()
        self.ocr_engine = OCREngine()
        self.face_detector = FaceDetector()
        self.hash_engine = PerceptualHash()
        self.stego_engine = StegoCheck()
        self.reverse_search = ReverseSearch()
        self.object_detector = ObjectDetector()
        self.intelligence_engine = ImageIntelligence()
        self.base_dir = base_dir

    def run(self, image_path: str) -> Dict[str, Any]:
        """
        Run complete image intelligence pipeline.
        Returns consolidated results dictionary.
        """
        # Validate file
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        filename = os.path.basename(image_path)

        # Execute all engines (each is isolated, won't crash)
        print("[INFO] Running EXIF extraction...")
        exif_data = self.exif_engine.extract_exif(image_path)

        print("[INFO] Running OCR text extraction...")
        ocr_data = self.ocr_engine.extract_text(image_path)

        print("[INFO] Running face detection...")
        face_data = self.face_detector.detect_faces(image_path)

        print("[INFO] Generating perceptual hash...")
        hash_data = self.hash_engine.generate_hash(image_path)

        print("[INFO] Checking steganography...")
        stego_data = self.stego_engine.check_steganography(image_path)

        print("[INFO] Running reverse image search...")
        search_data = self.reverse_search.search(image_path)

        print("[INFO] Running object detection...")
        object_data = self.object_detector.detect_objects(image_path)

        # Tampilkan link reverse search
        console.print("\n[bold cyan]🔍 Reverse Image Search Platforms:[/bold cyan]")
        for sr in search_data:
            console.print(f"  🔗 {sr['platform']}: {sr['url']}")

        # Consolidate
        results = {
            "filename": filename,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "exif": exif_data,
            "ocr": ocr_data,
            "faces": face_data,
            "hash": hash_data,
            "steganography": stego_data,
            "reverse_search": search_data,
            "object_detection": object_data,
        }

        # Calculate intelligence score
        score = self.intelligence_engine.calculate(results)
        results["intelligence_score"] = score

        return results

    def display_terminal_report(self, results: Dict) -> None:
        """Display rich terminal report."""
        console.print(
            Panel("[bold cyan]OSINT IMAGE INTELLIGENCE REPORT[/bold cyan]", border_style="cyan")
        )

        # Summary table
        table = Table(border_style="cyan")
        table.add_column("Engine", style="bold white")
        table.add_column("Status", style="cyan")
        table.add_column("Findings", style="white")

        # EXIF
        exif = results["exif"]
        gps_status = exif.get("gps", "NOT_FOUND")
        camera = exif.get("camera", "N/A")
        datetime_str = exif.get("datetime", "N/A")
        exif_findings = []
        if gps_status == "FOUND":
            exif_findings.append("GPS coordinates found")
        if camera:
            exif_findings.append(f"Camera: {camera}")
        if datetime_str:
            exif_findings.append(f"Date: {datetime_str}")
        table.add_row(
            "EXIF Metadata",
            "[green]FOUND[/green]" if exif_findings else "[yellow]NOT_FOUND[/yellow]",
            ", ".join(exif_findings) if exif_findings else "No metadata",
        )

        # OCR
        ocr = results["ocr"]
        ocr_findings = []
        if ocr.get("emails"):
            ocr_findings.append(f"{len(ocr['emails'])} email(s)")
        if ocr.get("phones"):
            ocr_findings.append(f"{len(ocr['phones'])} phone(s)")
        if ocr.get("usernames"):
            ocr_findings.append(f"{len(ocr['usernames'])} username(s)")
        if ocr.get("urls"):
            ocr_findings.append(f"{len(ocr['urls'])} URL(s)")
        table.add_row(
            "OCR",
            "[green]FOUND[/green]" if ocr_findings else "[yellow]NOT_FOUND[/yellow]",
            ", ".join(ocr_findings) if ocr_findings else "No text found",
        )

        # Faces
        faces = results["faces"]
        face_count = faces.get("faces_detected", 0)
        table.add_row(
            "Face Detection",
            "[green]FOUND[/green]" if face_count > 0 else "[yellow]NOT_FOUND[/yellow]",
            f"{face_count} face(s) detected" if face_count else "No faces",
        )

        # Hash
        hash_data = results["hash"]
        hash_value = hash_data.get("hash", "N/A")
        table.add_row(
            "Perceptual Hash",
            "[green]FOUND[/green]" if hash_value else "[red]ERROR[/red]",
            hash_value[:20] + "..." if len(hash_value) > 20 else hash_value,
        )

        # Steganography
        stego = results["steganography"]
        table.add_row(
            "Steganography",
            "[red]SUSPICIOUS[/red]" if stego.get("suspicious") == "True" else "[green]CLEAN[/green]",
            f"Entropy: {stego.get('entropy_score', 0):.4f}",
        )

        # Reverse Search
        search_count = len(results["reverse_search"])
        table.add_row(
            "Reverse Search",
            "[green]READY[/green]",
            f"{search_count} platform(s) available – links displayed above",
        )

        # Object Detection
        table.add_row(
            "Object Detection",
            "[yellow]NOT_IMPLEMENTED[/yellow]",
            "Future: YOLO, HuggingFace Vision",
        )

        console.print(table)

        # Intelligence score
        score = results.get("intelligence_score", 0)
        score_color = "green" if score > 50 else "yellow" if score > 20 else "red"
        console.print(
            f"\n[bold]Intelligence Score: [{score_color}]{score:.1f}/100[/{score_color}][/bold]"
        )

        # Quick summary
        found_count = sum(
            [
                1 if exif_findings else 0,
                1 if ocr_findings else 0,
                1 if face_count > 0 else 0,
                1 if stego.get("suspicious") == "True" else 0,
                1 if search_count > 0 else 0,
            ]
        )
        console.print(f"[INFO] Engines with findings: {found_count}/7\n")

    def export_results(self, results: Dict, target_name: str) -> str:
        """
        Export all results to files inside <base_dir>/results/image/<target_name>/.
        """
        output_dir = os.path.join(self.base_dir, "results", "image", target_name)
        os.makedirs(output_dir, exist_ok=True)

        # 1. JSON report
        json_path = os.path.join(output_dir, "image_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        # 2. Markdown report
        md_path = os.path.join(output_dir, "image_report.md")
        md_content = self._generate_markdown(results, target_name)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 3. CSV details
        csv_path = os.path.join(output_dir, "image_details.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Field", "Value"])
            # EXIF
            for key, val in results["exif"].items():
                if not isinstance(val, (dict, list)):
                    writer.writerow(["EXIF", key, val])
            # OCR
            ocr = results["ocr"]
            writer.writerow(["OCR", "raw_text", ocr.get("raw_text", "")[:200]])
            writer.writerow(["OCR", "emails", json.dumps(ocr.get("emails", []))])
            writer.writerow(["OCR", "phones", json.dumps(ocr.get("phones", []))])
            writer.writerow(["OCR", "usernames", json.dumps(ocr.get("usernames", []))])
            writer.writerow(["OCR", "urls", json.dumps(ocr.get("urls", []))])
            # Faces
            writer.writerow(["Faces", "count", results["faces"].get("faces_detected", 0)])
            writer.writerow(["Faces", "coordinates", json.dumps(results["faces"].get("coordinates", []))])
            # Hash
            for key, val in results["hash"].items():
                writer.writerow(["Hash", key, val])
            # Stego
            writer.writerow(["Stego", "suspicious", results["steganography"].get("suspicious", "False")])
            writer.writerow(["Stego", "entropy", results["steganography"].get("entropy_score", 0)])
            # Reverse Search
            for sr in results["reverse_search"]:
                writer.writerow(["Reverse Search", sr["platform"], sr["url"]])
            # Intelligence score
            writer.writerow(["Score", "intelligence_score", results.get("intelligence_score", 0)])

        # 4. Extracted text
        text_path = os.path.join(output_dir, "extracted_text.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(results["ocr"].get("raw_text", "No text extracted"))

        # 5. Metadata JSON
        meta_path = os.path.join(output_dir, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(results["exif"], f, indent=2, ensure_ascii=False, default=str)

        # 6. Faces JSON
        faces_path = os.path.join(output_dir, "faces.json")
        with open(faces_path, "w", encoding="utf-8") as f:
            json.dump(results["faces"], f, indent=2, ensure_ascii=False)

        console.print(f"[SUCCESS] Results exported to {output_dir}")
        return output_dir

    def _generate_markdown(self, results: Dict, target_name: str) -> str:
        """Generate professional markdown report."""
        md = f"""# OSINT Image Intelligence Report

**Image:** {target_name}
**Scan Time:** {results['timestamp']}
**Intelligence Score:** {results.get('intelligence_score', 0):.1f}/100

---

## EXIF Metadata

| Field | Value |
|-------|-------|
| Camera | {results['exif'].get('camera', 'N/A')} |
| GPS | {results['exif'].get('gps', 'NOT_FOUND')} |
| DateTime | {results['exif'].get('datetime', 'N/A')} |
| Software | {results['exif'].get('software', 'N/A')} |
| Resolution | {results['exif'].get('resolution', 'N/A')} |

"""
        # GPS details
        gps = results["exif"].get("gps_details", {})
        if gps:
            md += f"""
### GPS Coordinates
- Latitude: {gps.get('latitude', 'N/A')}
- Longitude: {gps.get('longitude', 'N/A')}
- Maps Link: {gps.get('maps_link', 'N/A')}

"""

        # OCR Findings
        ocr = results["ocr"]
        md += f"""## OCR Findings

### Extracted Text (first 500 chars)
{ocr.get('raw_text', 'No text extracted')[:500]}

### Detected Entities
"""
        if ocr.get("emails"):
            md += f"- **Emails:** {', '.join(ocr['emails'][:10])}\n"
        if ocr.get("phones"):
            md += f"- **Phones:** {', '.join(ocr['phones'][:10])}\n"
        if ocr.get("usernames"):
            md += f"- **Usernames:** {', '.join(ocr['usernames'][:10])}\n"
        if ocr.get("urls"):
            md += f"- **URLs:** {', '.join(ocr['urls'][:10])}\n"
        if not any([ocr.get("emails"), ocr.get("phones"), ocr.get("usernames"), ocr.get("urls")]):
            md += "No entities detected.\n"

        # Face Detection
        md += f"""
## Face Detection
- **Faces Detected:** {results['faces'].get('faces_detected', 0)}
"""
        if results["faces"].get("faces_detected", 0) > 0:
            md += f"- **Coordinates:** {results['faces']['coordinates']}\n"

        # Perceptual Hash
        h = results["hash"]
        md += f"""
## Perceptual Hash
- **pHASH:** {h.get('phash', 'N/A')}
- **dHash:** {h.get('dhash', 'N/A')}
- **aHash:** {h.get('ahash', 'N/A')}

"""

        # Steganography
        s = results["steganography"]
        md += f"""## Steganography Check
- **Suspicious:** {s.get('suspicious', 'False')}
- **Entropy Score:** {s.get('entropy_score', 0):.4f}

"""

        # Reverse Search
        md += """## Reverse Image Search
**Status:** READY
**Platforms:**
"""
        for sr in results["reverse_search"]:
            md += f"- [{sr['platform']}]({sr['url']})\n"

        md += """

### Instructions
1. Click any link above
2. Upload the image manually (drag & drop)
3. Analyze the results

"""

        # Object Detection
        md += """## Object Detection
- **Status:** NOT_IMPLEMENTED

---

**Report Generated by OSINT Fusion**
"""
        return md