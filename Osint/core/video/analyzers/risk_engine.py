# core/video/analyzers/risk_engine.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger

# Coba impor Google Cloud Vision
try:
    from google.cloud import vision
    _gcv_available = True
except ImportError:
    _gcv_available = False

# Environment variable untuk Vision API sudah dimuat oleh main.py
# melalui load_dotenv, sehingga tidak perlu memuat ulang di sini.


class RiskEngine:
    """
    Risk Assessment Engine untuk Video Intelligence.
    Menghitung Threat Score, Exposure Score, Confidence Score,
    dan Investigation Priority berdasarkan semua temuan.
    Dilengkapi deteksi konten sensitif via Google Cloud Vision SafeSearch.
    """

    # Bobot faktor risiko (total = 100 sebagai dasar normalisasi)
    RISK_FACTORS = {
        # GPS & Lokasi
        "gps_present": 10,
        "sensitive_country": 15,
        "government_building": 20,
        "military_facility": 30,
        "critical_infrastructure": 25,
        "airport_port": 15,
        
        # Objek Berbahaya
        "weapon_detected": 35,
        "military_vehicle": 25,
        "drone_detected": 15,
        "explosive_material": 40,
        
        # Informasi Pribadi
        "personal_email": 10,
        "personal_phone": 10,
        "identity_document": 20,
        "multiple_faces": 10,
        "crowd_detected": 15,
        
        # Metadata Mencurigakan
        "metadata_tampering": 20,
        "metadata_removal": 15,
        "re_encoded": 10,
        
        # Environment
        "night_scene": 5,
        "adverse_weather": 5,
        "isolated_location": 10,
        "indoor_restricted": 5,
        
        # Korelasi
        "darkweb_mention": 40,
        "known_threat_actor": 50,
        "sanctioned_entity": 35,

        # Konten Sensitif (SafeSearch)
        "adult_content": 25,
        "violence_content": 30,
        "medical_content": 10,
        "racy_content": 15,
    }

    # Keyword lokasi sensitif
    SENSITIVE_LOCATIONS = {
        "government": [
            "government", "parliament", "white house", "kremlin", "pentagon",
            "istana negara", "gedung dpr", "senayan", "capitol", "congress",
            "presidential palace", "governor", "ministry", "kementerian",
        ],
        "military": [
            "military", "army", "navy", "air force", "marines", "barracks",
            "tentara", "angkatan", "komando", "batalyon", "divisi", "brigade",
            "ammunition", "arsenal", "weapons depot",
        ],
        "critical_infra": [
            "power plant", "nuclear", "dam", "bendungan", "water treatment",
            "electric grid", "substation", "pipeline", "refinery", "kilang",
            "telecommunication tower", "data center",
        ],
        "airport_port": [
            "airport", "bandara", "runway", "terminal", "hangar",
            "port", "harbour", "pelabuhan", "dock", "container",
        ],
    }

    # Objek berbahaya dari YOLO classes
    DANGEROUS_OBJECT_MAP = {
        "weapon": ["knife", "scissors", "baseball bat", "bottle", "fork"],
        "military_vehicle": ["airplane", "truck", "boat", "helicopter"],
        "drone": ["bird", "kite"],  # proxy: drone sering terdeteksi sebagai burung
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self._gcv_client = None
        self._use_gcv = _gcv_available
        if self._use_gcv:
            try:
                self._gcv_client = vision.ImageAnnotatorClient()
                self.logger.info("Google Cloud Vision SafeSearch siap untuk Risk Engine")
            except Exception as e:
                self.logger.warning(f"Gagal inisialisasi Vision: {e}. SafeSearch tidak aktif.")
                self._use_gcv = False

    def analyze(
        self,
        metadata_result: Optional[ScanResult] = None,
        ocr_result: Optional[ScanResult] = None,
        face_result: Optional[ScanResult] = None,
        object_result: Optional[ScanResult] = None,
        environment_result: Optional[ScanResult] = None,
        geolocation_result: Optional[ScanResult] = None,
        language_result: Optional[ScanResult] = None,
        frame_paths: Optional[List[str]] = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Analisis risiko dari semua hasil, termasuk SafeSearch pada frame.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        detected_factors = []
        risk_score = 0
        exposure_score = 0
        confidence = 0.85

        # --- 0. SafeSearch (jika Vision tersedia) ---
        if self._use_gcv and frame_paths:
            risk_score, detected_factors = self._assess_safesearch(
                frame_paths[:5], risk_score, detected_factors
            )

        # --- 1. Metadata Analysis ---
        if metadata_result and metadata_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_metadata(
                metadata_result, risk_score, exposure_score, detected_factors
            )

        # --- 2. OCR Text Analysis ---
        if ocr_result and ocr_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_ocr(
                ocr_result, risk_score, exposure_score, detected_factors
            )

        # --- 3. Face Analysis ---
        if face_result and face_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_faces(
                face_result, risk_score, exposure_score, detected_factors
            )

        # --- 4. Object Analysis ---
        if object_result and object_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_objects(
                object_result, risk_score, exposure_score, detected_factors
            )

        # --- 5. Environment Analysis ---
        if environment_result and environment_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_environment(
                environment_result, risk_score, exposure_score, detected_factors
            )

        # --- 6. Geolocation Analysis ---
        if geolocation_result and geolocation_result.status == "FOUND":
            risk_score, exposure_score, detected_factors = self._assess_geolocation(
                geolocation_result, risk_score, exposure_score, detected_factors
            )

        # --- 7. Normalisasi & Level ---
        risk_score = min(int(risk_score), 100)
        exposure_score = min(int(exposure_score), 100)

        if risk_score >= 75:
            threat_level = "CRITICAL"
            priority = "IMMEDIATE"
        elif risk_score >= 50:
            threat_level = "HIGH"
            priority = "HIGH"
        elif risk_score >= 25:
            threat_level = "MEDIUM"
            priority = "MEDIUM"
        elif risk_score >= 10:
            threat_level = "LOW"
            priority = "LOW"
        else:
            threat_level = "MINIMAL"
            priority = "NONE"

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Risk Assessment",
            username=filename,
            status="FOUND" if detected_factors else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=confidence,
            extra={
                "threat_score": risk_score,
                "exposure_score": exposure_score,
                "confidence_score": confidence,
                "threat_level": threat_level,
                "investigation_priority": priority,
                "factors_detected": detected_factors,
                "factor_count": len(detected_factors),
                "analysis_time_seconds": analysis_time,
                "method": "Multi-factor risk assessment engine + SafeSearch",
            },
        )

    def _assess_safesearch(self, frame_paths: List[str], risk_score: int, factors: List[str]) -> tuple:
        """Deteksi konten sensitif menggunakan Vision SafeSearch."""
        adult = violence = medical = racy = 0
        for fp in frame_paths:
            if not os.path.isfile(fp):
                continue
            try:
                with open(fp, "rb") as f:
                    content = f.read()
                image = vision.Image(content=content)
                response = self._gcv_client.safe_search_detection(image=image)
                safe = response.safe_search_annotation
                if safe.adult >= 3:
                    adult += 1
                    risk_score += self.RISK_FACTORS["adult_content"]
                if safe.violence >= 3:
                    violence += 1
                    risk_score += self.RISK_FACTORS["violence_content"]
                if safe.medical >= 3:
                    medical += 1
                    risk_score += self.RISK_FACTORS["medical_content"]
                if safe.racy >= 3:
                    racy += 1
                    risk_score += self.RISK_FACTORS["racy_content"]
            except Exception as e:
                self.logger.warning(f"SafeSearch gagal untuk {fp}: {e}")

        if adult > 0:
            factors.append(f"Adult content detected in {adult} frames")
        if violence > 0:
            factors.append(f"Violence content detected in {violence} frames")
        if medical > 0:
            factors.append(f"Medical content detected in {medical} frames")
        if racy > 0:
            factors.append(f"Racy content detected in {racy} frames")
        return risk_score, factors

    # ---------- Sub-Assessors (tetap sama seperti sebelumnya) ----------

    def _assess_metadata(self, result, risk, exposure, factors):
        extra = result.extra or {}
        integrity = extra.get("integrity_check", {})
        if integrity.get("suspicious"):
            risk += self.RISK_FACTORS["metadata_tampering"]
            factors.append("Metadata tampering detected")
            findings = integrity.get("findings", [])
            if "removal" in " ".join(findings).lower():
                risk += self.RISK_FACTORS["metadata_removal"]
                factors.append("Metadata removal suspected")
        gps = extra.get("gps", {})
        if gps and gps.get("raw"):
            risk += self.RISK_FACTORS["gps_present"]
            exposure += 15
            factors.append("GPS coordinates exposed")
        return risk, exposure, factors

    def _assess_ocr(self, result, risk, exposure, factors):
        extra = result.extra or {}
        full_text = extra.get("full_text", "").lower()
        
        for category, keywords in self.SENSITIVE_LOCATIONS.items():
            for kw in keywords:
                if kw in full_text:
                    if category == "government":
                        risk += self.RISK_FACTORS["government_building"]
                        factors.append(f"Government building reference: '{kw}'")
                    elif category == "military":
                        risk += self.RISK_FACTORS["military_facility"]
                        factors.append(f"Military facility reference: '{kw}'")
                    elif category == "critical_infra":
                        risk += self.RISK_FACTORS["critical_infrastructure"]
                        factors.append(f"Critical infrastructure reference: '{kw}'")
                    elif category == "airport_port":
                        risk += self.RISK_FACTORS["airport_port"]
                        factors.append(f"Airport/Port reference: '{kw}'")
                    break

        emails = extra.get("emails", [])
        phones = extra.get("phones", [])
        if emails:
            risk += min(len(emails) * self.RISK_FACTORS["personal_email"] // 5, 30)
            exposure += min(len(emails) * 10, 30)
            factors.append(f"Personal emails exposed: {len(emails)}")
        if phones:
            risk += min(len(phones) * self.RISK_FACTORS["personal_phone"] // 5, 20)
            exposure += min(len(phones) * 10, 20)
            factors.append(f"Personal phones exposed: {len(phones)}")

        return risk, exposure, factors

    def _assess_faces(self, result, risk, exposure, factors):
        total_faces = result.extra.get("total_faces", 0) if result.extra else 0
        if total_faces > 20:
            risk += self.RISK_FACTORS["crowd_detected"]
            exposure += 15
            factors.append(f"Crowd detected: {total_faces} faces")
        elif total_faces > 5:
            risk += self.RISK_FACTORS["multiple_faces"]
            exposure += 5
            factors.append(f"Multiple faces detected: {total_faces}")
        return risk, exposure, factors

    def _assess_objects(self, result, risk, exposure, factors):
        obj_counts = result.extra.get("object_counts", {}) if result.extra else {}
        for obj_name, count in obj_counts.items():
            obj_lower = obj_name.lower()
            if obj_lower in self.DANGEROUS_OBJECT_MAP["weapon"]:
                risk += self.RISK_FACTORS["weapon_detected"]
                factors.append(f"Weapon-like object: {obj_name} ({count})")
                break
            if obj_lower in self.DANGEROUS_OBJECT_MAP["military_vehicle"]:
                risk += self.RISK_FACTORS["military_vehicle"]
                factors.append(f"Military vehicle: {obj_name} ({count})")
                break
        return risk, exposure, factors

    def _assess_environment(self, result, risk, exposure, factors):
        extra = result.extra or {}
        if extra.get("time_of_day") == "night":
            risk += self.RISK_FACTORS["night_scene"]
            factors.append("Night scene")
        if extra.get("weather") in ["rainy", "foggy"]:
            risk += self.RISK_FACTORS["adverse_weather"]
            factors.append("Adverse weather")
        if extra.get("indoor_outdoor") == "indoor":
            risk += self.RISK_FACTORS["indoor_restricted"]
            factors.append("Indoor – potentially restricted area")
        return risk, exposure, factors

    def _assess_geolocation(self, result, risk, exposure, factors):
        cands = result.extra.get("candidates", []) if result.extra else []
        sensitive_countries = ["China", "Russia", "Iran", "North Korea", "Syria", "Afghanistan"]
        for c in cands:
            country = c.get("country", "")
            if country in sensitive_countries:
                risk += self.RISK_FACTORS["sensitive_country"]
                factors.append(f"Sensitive country: {country}")
                break
        return risk, exposure, factors