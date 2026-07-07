# core/video/providers/ffmpeg_provider.py
from __future__ import annotations

import os
import subprocess
import json
from typing import Dict, Any, Optional, List
from utils.logger import Logger


class FFmpegProvider:
    """Provider untuk operasi FFmpeg: metadata, frame extraction, audio extraction."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Ambil metadata video menggunakan ffprobe."""
        if not os.path.isfile(file_path):
            return {"error": "File not found"}

        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return self._parse_metadata(data)
            else:
                return {"error": result.stderr.strip()}
        except FileNotFoundError:
            return {"error": "FFmpeg not installed. Install from https://ffmpeg.org/"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_metadata(self, data: Dict) -> Dict[str, Any]:
        """Parse hasil ffprobe menjadi dictionary terstruktur."""
        fmt = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        # GPS metadata (jika ada)
        gps = {}
        tags = fmt.get("tags", {})
        for key in ["location", "com.apple.quicktime.location.ISO6709", "GPS coordinates"]:
            if key in tags:
                gps["raw"] = tags[key]

        return {
            "file_size_bytes": int(fmt.get("size", 0)),
            "duration_seconds": float(fmt.get("duration", 0)),
            "format_name": fmt.get("format_name", ""),
            "bitrate": int(fmt.get("bit_rate", 0)) if fmt.get("bit_rate") else 0,
            "tags": tags,
            "video": {
                "codec": video_stream.get("codec_name", ""),
                "resolution": f"{video_stream.get('width', '?')}x{video_stream.get('height', '?')}",
                "frame_rate": self._parse_frame_rate(video_stream.get("r_frame_rate", "")),
                "pix_fmt": video_stream.get("pix_fmt", ""),
            } if video_stream else {},
            "audio": {
                "codec": audio_stream.get("codec_name", ""),
                "sample_rate": audio_stream.get("sample_rate", 0),
                "channels": audio_stream.get("channels", 0),
            } if audio_stream else {},
            "gps": gps,
        }

    @staticmethod
    def _parse_frame_rate(rate_str: str) -> float:
        """Parse frame rate dari format '30000/1001' menjadi float."""
        try:
            if "/" in rate_str:
                num, den = rate_str.split("/")
                return float(num) / float(den)
            return float(rate_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def extract_audio(self, file_path: str, output_path: str) -> bool:
        """Ekstrak audio dari video ke file WAV."""
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-vn",  # no video
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            output_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return result.returncode == 0 and os.path.isfile(output_path)
        except Exception:
            return False

    def extract_frames(self, file_path: str, output_dir: str, interval: float = 2.0) -> List[str]:
        """Ekstrak keyframe setiap interval detik."""
        os.makedirs(output_dir, exist_ok=True)
        frames = []
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-vf", f"fps=1/{interval}",
            "-qscale:v", "2",
            f"{output_dir}/frame_%04d.jpg",
            "-y"
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            frames = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.startswith("frame_") and f.endswith(".jpg")
            ])
        except Exception:
            pass
        return frames