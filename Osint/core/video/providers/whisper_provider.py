# core/video/providers/whisper_provider.py
from __future__ import annotations

import os
from typing import Dict, Any, Optional
from utils.logger import Logger


class WhisperProvider:
    """
    Provider untuk transkripsi audio menggunakan Faster-Whisper (offline).
    Jika tidak tersedia, fallback ke whisper (openai-whisper).
    """

    def __init__(self, base_dir: str = "Osint", model_size: str = "tiny"):
        self.logger = Logger(base_dir=base_dir)
        self.model = None
        self.model_size = model_size
        self._load_model()

    def _load_model(self):
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
            self.logger.info(f"Faster-Whisper model '{self.model_size}' loaded")
        except ImportError:
            self.logger.warning("faster-whisper not installed, trying openai-whisper...")
            try:
                import whisper
                self.model = whisper.load_model(self.model_size)
                self.logger.info(f"OpenAI-Whisper model '{self.model_size}' loaded")
            except ImportError:
                self.logger.error("No Whisper implementation found. Install: pip install faster-whisper")
                self.model = None
            except Exception as e:
                self.logger.error(f"Failed to load Whisper: {e}")
                self.model = None
        except Exception as e:
            self.logger.error(f"Failed to load Faster-Whisper: {e}")
            self.model = None

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transkripsi file audio ke teks.
        Mengembalikan dictionary dengan 'text', 'language', 'segments'.
        """
        if not self.model:
            return {"text": "", "language": "", "segments": [], "error": "Model not loaded"}

        if not os.path.isfile(audio_path):
            return {"text": "", "language": "", "segments": [], "error": "Audio file not found"}

        try:
            # Deteksi jenis model
            if hasattr(self.model, "transcribe") and callable(self.model.transcribe):
                # faster-whisper
                segments, info = self.model.transcribe(audio_path, beam_size=5)
                full_text = " ".join([seg.text for seg in segments])
                return {
                    "text": full_text,
                    "language": info.language,
                    "segments": [{"start": seg.start, "end": seg.end, "text": seg.text} for seg in segments],
                }
            elif hasattr(self.model, "transcribe"):
                # openai-whisper
                result = self.model.transcribe(audio_path)
                return {
                    "text": result.get("text", ""),
                    "language": result.get("language", ""),
                    "segments": result.get("segments", []),
                }
            else:
                return {"text": "", "language": "", "segments": [], "error": "Unknown model type"}
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {"text": "", "language": "", "segments": [], "error": str(e)}