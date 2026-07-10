import json
import os
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_CATEGORIES = {
    "Documentos": {
        "DOC": [".doc", ".docx"],
        "PDF": [".pdf"],
        "TXT": [".txt"],
        "PLANILHAS": [".xls", ".xlsx", ".csv"],
        "APRESENTACOES": [".ppt", ".pptx"]
    },
    "Imagens": {
        "JPG": [".jpeg", ".jpg"],
        "PNG": [".png"],
        "GIF": [".gif"],
        "SVG": [".svg"],
        "RAW": [".raw", ".cr2", ".nef"]
    },
    "Vídeos": {
        "MP4": [".mp4"],
        "AVI": [".avi"],
        "MOV": [".mov"],
        "MKV": [".mkv"],
        "WMV": [".wmv"]
    },
    "Áudio": {
        "MP3": [".mp3"],
        "WAV": [".wav"],
        "FLAC": [".flac"],
        "AAC": [".aac"]
    },
    "Compactados": {
        "ZIP": [".zip"],
        "RAR": [".rar"],
        "7Z": [".7z"],
        "TAR": [".tar"],
        "GZ": [".gz"]
    },
    "Executáveis": {
        "EXE": [".exe"],
        "MSI": [".msi"],
        "BAT": [".bat"]
    },
    "Scripts": {
        "PYTHON": [".py", ".pyw"],
        "RUBY": [".rb"],
        "JAVASCRIPT": [".js"],
        "TYPESCRIPT": [".ts"],
        "PHP": [".php"],
        "JAVA": [".java"],
        "CSHARP": [".cs"],
        "GO": [".go"]
    },
    "Banco de Dados": {
        "SQL": [".sql"],
        "SQLITE": [".sqlite", ".sqlite3"],
        "DB": [".db"],
        "MDB": [".mdb"]
    },
    "ISO": {
        "ISO": [".iso"],
        "IMG": [".img"]
    }
}

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_path = Path(config_file)
        self.config = self._load_default_config()
        self.load()

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "monitored_folders": [
                str(Path.home() / "Desktop"),
                str(Path.home() / "Downloads"),
                str(Path.home() / "Documents")
            ],
            "categories": DEFAULT_CATEGORIES,
            "whitelist": [],
            "blacklist": [
                ".tmp", ".temp", ".crdownload", ".part"
            ],
            "check_interval": 1.0,
            "auto_start": True
        }

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get_extension_destination(self, ext: str) -> tuple[str, str]:
        ext = ext.lower()
        for category, subcategories in self.config["categories"].items():
            for subcat, exts in subcategories.items():
                if ext in exts:
                    return category, subcat
        return "Outros", ext[1:].upper() if ext else "DESCONHECIDO"

    def get_monitored_folders(self) -> List[str]:
        return self.config.get("monitored_folders", [])
    
    def add_monitored_folder(self, folder_path: str):
        if folder_path not in self.config["monitored_folders"]:
            self.config["monitored_folders"].append(folder_path)
            self.save()

    def remove_monitored_folder(self, folder_path: str):
        if folder_path in self.config["monitored_folders"]:
            self.config["monitored_folders"].remove(folder_path)
            self.save()

    def is_allowed(self, filename: str) -> bool:
        ext = Path(filename).suffix.lower()
        if ext in self.config.get("blacklist", []):
            return False
        if self.config.get("whitelist"):
            return ext in self.config["whitelist"]
        return True
