from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileEvent:
    filepath: str
    event_type: str
    timestamp: datetime = datetime.now()

@dataclass
class HistoryRecord:
    id: int = 0
    date: str = ""
    time: str = ""
    filename: str = ""
    origin: str = ""
    destination: str = ""
    category: str = ""
    username: str = ""
    size_bytes: int = 0
    file_hash: str = ""
