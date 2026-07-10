import time
import queue
import logging
import threading
from pathlib import Path

try:
    from plyer import notification
except ImportError:
    notification = None

from .models import FileEvent, HistoryRecord
from .utils import safe_move, get_file_hash, is_file_in_use
import os

class OrganizerWorker(threading.Thread):
    def __init__(self, event_queue: queue.Queue, config_manager, db_manager, ai_analyzer):
        super().__init__(daemon=True)
        self.event_queue = event_queue
        self.config = config_manager
        self.db = db_manager
        self.ai = ai_analyzer
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                event: FileEvent = self.event_queue.get(timeout=1.0)
                self.process_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Erro inesperado no OrganizerWorker: {e}")

    def process_event(self, event: FileEvent):
        filepath = Path(event.filepath)
        time.sleep(1)
        if not filepath.exists(): return
            
        retries = 5
        while retries > 0 and is_file_in_use(str(filepath)):
            time.sleep(1)
            retries -= 1
            
        if is_file_in_use(str(filepath)):
            logging.warning(f"Arquivo ignorado pois está em uso prolongado: {filepath}")
            return

        try:
            ext = filepath.suffix.lower()
            if not ext: ext = self.ai.get_real_extension(filepath)
            category, subcategory = self.config.get_extension_destination(ext)
            if category == "Outros" and subcategory == "DESCONHECIDO":
                category, subcategory = self.ai.suggest_category_for_unknown(filepath)
            
            dest_folder = filepath.parent / category / subcategory
            size = filepath.stat().st_size
            file_hash = get_file_hash(filepath) or ""
            
            final_dest = safe_move(filepath, dest_folder, fallback_ext=ext)
            
            record = HistoryRecord(
                date=event.timestamp.strftime("%Y-%m-%d"), time=event.timestamp.strftime("%H:%M:%S"),
                filename=filepath.name, origin=str(filepath), destination=final_dest,
                category=f"{category}/{subcategory}", username=os.getlogin(),
                size_bytes=size, file_hash=file_hash
            )
            self.db.insert_record(record)
            logging.info(f"Arquivo movido: {filepath.name} -> {final_dest}")
            
            if notification:
                try:
                    notification.notify(
                        title="Arquivo Organizado",
                        message=f"{filepath.name} movido para {category}",
                        app_name="Assistente de Organização", timeout=3
                    )
                except Exception:
                    pass
        except Exception as e:
            logging.error(f"Erro ao processar {filepath}: {e}")

    def scan_directories_now(self):
        for folder in self.config.get_monitored_folders():
            path = Path(folder)
            if not path.exists(): continue
            for item in path.iterdir():
                if item.is_file():
                    self.event_queue.put(FileEvent(filepath=str(item), event_type='scan'))
