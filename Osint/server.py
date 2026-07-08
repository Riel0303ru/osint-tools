# server.py
import os
import shutil
import math
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environmental configs first
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env.local")
load_dotenv()  # Fallback to standard .env

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# OSINT Core Imports
from core.base.scan_manager import ScanManager
from core.correlation.correlation_workflow import CorrelationWorkflow
from core.ai.ai_workflow import AIWorkflow
from core.report.report_generator import ReportGenerator

# Initialize FastAPI App with automatic Swagger/ReDoc docs enabled
app = FastAPI(
    title="OSINT Fusion API",
    description="REST API server wrapping the Python OSINT advanced scanner workflows.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate central scan manager
scan_manager = ScanManager(base_dir="Osint")

# Setup uploads storage directory
UPLOAD_DIR = Path("Osint") / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# RESPONSE FORMAT HELPERS
# =========================================================

def success_response(data: Any = None, message: str = "Success") -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "error_code": None
    }


def error_response(message: str, error_code: str = "ERR_INTERNAL_SERVER_ERROR") -> dict:
    return {
        "success": False,
        "data": None,
        "message": message,
        "error_code": error_code
    }


def save_uploaded_file(upload_file: UploadFile) -> str:
    """Utility to save multipart uploads to disk for pipeline workflow scanners."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', upload_file.filename or "file")
    target_path = UPLOAD_DIR / filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return str(target_path)


# =========================================================
# REQUEST SCHEMAS
# =========================================================

class UsernameScanRequest(BaseModel):
    username: str
    budget: int = 100
    priority_platforms: List[str] = []


class EmailScanRequest(BaseModel):
    email: str


class DomainScanRequest(BaseModel):
    domain: str


class PhoneScanRequest(BaseModel):
    phone: str


class IPScanRequest(BaseModel):
    ip: str


class CompanyScanRequest(BaseModel):
    domain: str


class DarkwebScanRequest(BaseModel):
    target: str


class AIAnalyzeRequest(BaseModel):
    target_id: Optional[str] = None
    prompt: str
    module_name: Optional[str] = None


class ReportGenerateRequest(BaseModel):
    target: str


# =========================================================
# API ROUTES
# =========================================================

@app.get("/health")
def health_check():
    return success_response(message="OSINT Fusion server is healthy.")


@app.post("/api/scan/username")
async def api_scan_username(req: UsernameScanRequest):
    if not req.username.strip():
        return error_response("Username cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_username_workflow(
            username=req.username,
            budget=req.budget,
            priority_platforms=req.priority_platforms
        )
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/email")
async def api_scan_email(req: EmailScanRequest):
    if not req.email.strip():
        return error_response("Email cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_email_workflow(req.email)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/domain")
async def api_scan_domain(req: DomainScanRequest):
    if not req.domain.strip():
        return error_response("Domain cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_domain_workflow(req.domain)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/phone")
async def api_scan_phone(req: PhoneScanRequest):
    if not req.phone.strip():
        return error_response("Phone cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_phone_workflow(req.phone)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/ip")
async def api_scan_ip(req: IPScanRequest):
    if not req.ip.strip():
        return error_response("IP cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_ip_workflow(req.ip)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/company")
async def api_scan_company(req: CompanyScanRequest):
    if not req.domain.strip():
        return error_response("Domain cannot be empty", "ERR_INVALID_INPUT")
    try:
        results, full_report = await scan_manager.execute_company_workflow(req.domain)
        return success_response({
            "results": [r.to_dict() for r in results],
            "report": full_report
        })
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/darkweb")
async def api_scan_darkweb(req: DarkwebScanRequest):
    if not req.target.strip():
        return error_response("Target cannot be empty", "ERR_INVALID_INPUT")
    try:
        results = await scan_manager.execute_darkweb_workflow(req.target)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/image")
async def api_scan_image(file: UploadFile = File(...)):
    try:
        temp_path = save_uploaded_file(file)
        results = await scan_manager.execute_image_workflow(temp_path)
        # Results is returned as list of ScanResult from execute_image_workflow
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/document")
async def api_scan_document(file: UploadFile = File(...)):
    try:
        temp_path = save_uploaded_file(file)
        results = await scan_manager.execute_document_workflow(temp_path)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/scan/video")
async def api_scan_video(file: UploadFile = File(...)):
    try:
        temp_path = save_uploaded_file(file)
        results = await scan_manager.execute_video_workflow(temp_path)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/ai/analyze")
async def api_ai_analyze(req: AIAnalyzeRequest):
    try:
        ai_workflow = AIWorkflow()
        if req.target_id:
            # Load latest results from storage
            results = scan_manager.storage.get_latest_scan(req.target_id)
            if not results:
                return error_response(f"No scan history found for target '{req.target_id}'", "ERR_NOT_FOUND")
            
            # Format results as dicts for compatibility
            results_dicts = [r.to_dict() for r in results]
            analysis = await ai_workflow.execute(req.target_id, req.module_name or "general", results_dicts)
            return success_response(analysis)
        else:
            # General prompt chatbot fallback
            response = await ai_workflow.analyzer.analyze(req.prompt)
            if not response.get("success"):
                return error_response(response.get("error", "AI Analysis failed"), "ERR_AI_API")
            return success_response(response.get("analysis"))
    except Exception as e:
        return error_response(str(e))


@app.get("/api/correlation")
def api_correlation(target: Optional[str] = Query(None)):
    try:
        wf = CorrelationWorkflow(scan_manager.storage, base_dir="Osint")
        results = wf.execute_all()
        
        if "error" in results:
            return error_response(results["error"], "ERR_NO_DATA")

        # Implement user requested target-based sub-graph filtering
        if target:
            target_clean = target.strip().lower()
            nodes = results.get("graph", {}).get("nodes", [])
            edges = results.get("graph", {}).get("edges", [])
            
            matching_ids = set()
            for n in nodes:
                # Matches either the entity name or specific platform identifier
                if target_clean in n.get("entity", "").lower() or target_clean in n.get("id", "").lower():
                    matching_ids.add(n["id"])
            
            connected_ids = set(matching_ids)
            filtered_edges = []
            for e in edges:
                if e["source"] in matching_ids or e["target"] in matching_ids:
                    filtered_edges.append(e)
                    connected_ids.add(e["source"])
                    connected_ids.add(e["target"])

            filtered_nodes = [n for n in nodes if n["id"] in connected_ids]
            
            results["graph"] = {
                "nodes": filtered_nodes,
                "edges": filtered_edges,
                "total_nodes": len(filtered_nodes),
                "total_edges": len(filtered_edges),
            }
        
        return success_response(results)
    except Exception as e:
        return error_response(str(e))


@app.get("/api/history")
def api_get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        items = scan_manager.storage.get_paginated_history(page, limit)
        total = scan_manager.storage.get_total_history_count()
        pages = math.ceil(total / limit)
        
        return success_response({
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        })
    except Exception as e:
        return error_response(str(e))


@app.get("/api/history/{target}")
def api_get_target_history(target: str):
    try:
        timestamps = scan_manager.storage.get_distinct_timestamps(target)
        return success_response(timestamps)
    except Exception as e:
        return error_response(str(e))


@app.get("/api/history/{target}/{timestamp}")
def api_get_snapshot(target: str, timestamp: str):
    try:
        results = scan_manager.storage.get_scan_snapshot(target, timestamp)
        return success_response([r.to_dict() for r in results])
    except Exception as e:
        return error_response(str(e))


@app.post("/api/reports/generate")
def api_generate_report(req: ReportGenerateRequest):
    if not req.target.strip():
        return error_response("Target cannot be empty", "ERR_INVALID_INPUT")
    try:
        report_gen = ReportGenerator(scan_manager.storage, base_dir="Osint")
        output_dir = report_gen.generate(req.target)
        
        pdf_name = "osint_report.pdf"
        pdf_path = output_dir / pdf_name
        
        return success_response({
            "target": req.target,
            "report_dir": str(output_dir),
            "pdf_generated": pdf_path.exists(),
            "download_url": f"/api/reports/download?target={req.target}"
        })
    except Exception as e:
        return error_response(str(e))


@app.get("/api/reports/download")
def api_download_report(target: str):
    if not target.strip():
        raise HTTPException(status_code=400, detail="Target required")
    
    # Sanitize name
    safe_target = re.sub(r'[<>:"/\\|?*]', '_', target)[:100]
    pdf_path = Path("Osint") / "results" / "reports" / safe_target / "osint_report.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report PDF not found. Generate it first.")
        
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"OSINT_Report_{safe_target}.pdf"
    )


@app.get("/api/dashboard/stats")
def api_dashboard_stats():
    try:
        # Collect statistics from all target scan results
        db = scan_manager.storage
        session = db.SessionLocal()
        
        total_unique_targets = db.get_total_history_count()
        
        # Calculate status distributions
        try:
            total_records = session.query(func.count(ScanResultModel.id)).scalar() or 0
            found_records = session.query(func.count(ScanResultModel.id)).filter(ScanResultModel.status == "FOUND").scalar() or 0
            error_records = session.query(func.count(ScanResultModel.id)).filter(ScanResultModel.status == "ERROR").scalar() or 0
        except Exception:
            total_records = 0
            found_records = 0
            error_records = 0
        
        # Calculate risk scores based on intelligence_score
        # safe: 0-20, low: 21-40, medium: 41-60, high: 61-80, critical: 81-100
        risk_counts = {"safe": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
        try:
            # Select max intelligence score per unique target to represent target threat risk
            subq = session.query(
                ScanResultModel.username,
                func.max(ScanResultModel.intelligence_score).label("max_score")
            ).group_by(ScanResultModel.username).subquery()
            
            scores = session.query(subq.c.max_score).all()
            for (score,) in scores:
                s = score or 0.0
                if s <= 20:
                    risk_counts["safe"] += 1
                elif s <= 40:
                    risk_counts["low"] += 1
                elif s <= 60:
                    risk_counts["medium"] += 1
                elif s <= 80:
                    risk_counts["high"] += 1
                else:
                    risk_counts["critical"] += 1
        except Exception:
            pass
        finally:
            session.close()

        # Gather recent scans for activity feed
        recent_scans = []
        try:
            # Query recent unique targets and timestamps
            cur = db.execute(
                "SELECT username, platform, status, scan_timestamp, intelligence_score FROM scan_results "
                "ORDER BY scan_timestamp DESC LIMIT 10"
            )
            for row in cur.fetchall():
                recent_scans.append({
                    "target": row["username"],
                    "platform": row["platform"],
                    "status": row["status"],
                    "timestamp": row["scan_timestamp"],
                    "score": row["intelligence_score"]
                })
        except Exception:
            pass

        return success_response({
            "targets_count": total_unique_targets,
            "scans_count": total_records,
            "found_count": found_records,
            "error_count": error_records,
            "risks": risk_counts,
            "recent_activity": recent_scans
        })
    except Exception as e:
        return error_response(str(e))
