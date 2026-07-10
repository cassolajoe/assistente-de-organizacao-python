import sys
import threading
import queue
import logging
from pathlib import Path
from PIL import Image
import pystray
from pystray import MenuItem as item

from .config import ConfigManager
from .database import DatabaseManager
from .ai import AIAnalyzer
from .watcher import FolderWatcher
from .organizer import OrganizerWorker
from .gui.dashboard import DashboardGUI

class AppCore:
    def __init__(self):
        Path("logs").mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("logs/app.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.config = ConfigManager()
        self.db = DatabaseManager()
        self.ai = AIAnalyzer()
        self.event_queue = queue.Queue()
        self.watcher = FolderWatcher(self.event_queue, self.config)
        self.watcher.start()
        self.worker = OrganizerWorker(self.event_queue, self.config, self.db, self.ai)
        self.worker.start()
        self.gui = DashboardGUI(self)

    def stop(self):
        logging.info("Encerrando aplicação...")
        self.watcher.stop()
        self.worker.stop()
        self.worker.join()
        self.gui.running = False
        sys.exit(0)

def create_image():
    img = Image.new('RGB', (64, 64), color=(0, 120, 215))
    return img

def main():
    core = AppCore()

    def show_app(icon, item):
        core.gui.show_window()

    def exit_app(icon, item):
        icon.stop()
        core.gui.root.quit()
        core.stop()

    menu = pystray.Menu(
        item('Abrir Dashboard', show_app, default=True),
        item('Sair', exit_app)
    )

    icon = pystray.Icon("Organizador", create_image(), "Assistente de Organização", menu)
    icon_thread = threading.Thread(target=icon.run, daemon=True)
    icon_thread.start()
    core.gui.run()

if __name__ == "__main__":
    main()
