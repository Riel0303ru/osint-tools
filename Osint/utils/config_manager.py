# utils/config_manager.py
from pathlib import Path
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

# Load variabel environment dari .env.local di root project
ENV_PATH = Path(__file__).resolve().parents[1] / ".env.local"
load_dotenv(ENV_PATH)


class ConfigManager:


    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.config_file = self.config_dir / "settings.json"

    @staticmethod
    def get_env(key: str, default: Any = None) -> Any:

        return os.getenv(key, default)

    def get_default_config(self) -> Dict[str, Any]:

        return {
            "project_name": "OSINT Fusion",
            "version": "1.0",
            "theme": {
                "primary_color": "cyan",
                "secondary_color": "green",
                "warning_color": "yellow",
                "error_color": "red"
            },
            "runtime": {
                "timeout": 10,
                "retries": 2,
                "verify_ssl": True
            },
            "output": {
                "folder": "outputs",
                "save_json": True,
                "save_txt": False,
                "save_html": False
            },
            "modules": {
                "username": True,
                "email": True,
                "domain": True,
                "phone": True,
                "image": True,
                "ai": True,
                "graph": True
            },
            "network": {
                "user_agent": "OSINT-Fusion/1.0"
            }
        }

    def ensure_config_exists(self) -> None:
  
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            default_config = self.get_default_config()
            self.save_config(default_config)

    def load_config(self) -> Dict[str, Any]:

        self.ensure_config_exists()

        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # Jika file rusak, kembalikan default config
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config

    def save_config(self, config_data: Dict[str, Any]) -> None:
 
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(config_data, file, indent=4, ensure_ascii=False)

    def update_config(self, section: str, key: str, value: Any) -> None:
   
        config = self.load_config()

        if section not in config:
            config[section] = {}

        if isinstance(config[section], dict):
            config[section][key] = value
            self.save_config(config)
        else:
            raise ValueError(f"Section '{section}' bukan dictionary.")

    def reset_config(self) -> None:
        self.save_config(self.get_default_config())