# test_vision.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env.local dari folder Osint/
env_path = Path(__file__).parent / ".env.local"
load_dotenv(dotenv_path=env_path)

from google.cloud import vision

client = vision.ImageAnnotatorClient()
print(" Google Cloud Vision client siap digunakan")