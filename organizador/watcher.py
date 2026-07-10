import time
import queue
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .models import FileEvent

class FolderWatcher(FileSystemEventHandler):
    def __init__(self, event_queue: queue.Queue, config_manager):
        super().__init__()
        self.event_queue = event_queue
        self.config_manager = config_manager
        self.observer = Observer()
        self.watches = {}

    def start(self):
        self._update_watches()
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def update_folders(self):
        self._update_watches()

    def _update_watches(self):
        current_folders = set(self.config_manager.get_monitored_folders())
        watching_folders = set(self.watches.keys())

        for folder in current_folders - watching_folders:
            path = Path(folder)
            if path.exists() and path.is_dir():
                try:
                    w = self.observer.schedule(self, str(path), recursive=False)
                    self.watches[str(path)] = w
                    logging.info(f"Monitorando: {path}")
                except Exception as e:
                    logging.error(f"Erro ao monitorar {path}: {e}")

        for folder in watching_folders - current_folders:
            w = self.watches.pop(folder)
            self.observer.unschedule(w)
            logging.info(f"Parou de monitorar: {folder}")

    def on_created(self, event):
        if not event.is_directory:
            self._queue_event(event.src_path, 'created')

    def on_moved(self, event):
        if not event.is_directory:
            self._queue_event(event.dest_path, 'moved')

    def _queue_event(self, filepath: str, event_type: str):
        if not self.config_manager.is_allowed(filepath):
            return
        evt = FileEvent(filepath=filepath, event_type=event_type)
        self.event_queue.put(evt)
