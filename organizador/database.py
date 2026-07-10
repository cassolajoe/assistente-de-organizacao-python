import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List
from .models import HistoryRecord

class DatabaseManager:
    def __init__(self, db_path: str = "database/history.db"):
        self.db_path = Path(db_path)
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    time TEXT,
                    filename TEXT,
                    origin TEXT,
                    destination TEXT,
                    category TEXT,
                    username TEXT,
                    size_bytes INTEGER,
                    file_hash TEXT
                )
            ''')
            conn.commit()

    def insert_record(self, record: HistoryRecord):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (date, time, filename, origin, destination, category, username, size_bytes, file_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.date, record.time, record.filename, record.origin,
                record.destination, record.category, record.username,
                record.size_bytes, record.file_hash
            ))
            conn.commit()

    def get_recent_history(self, limit: int = 100) -> List[HistoryRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, time, filename, origin, destination, category, username, size_bytes, file_hash 
                FROM history ORDER BY id DESC LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            records = []
            for row in rows:
                records.append(HistoryRecord(
                    id=row[0], date=row[1], time=row[2], filename=row[3], origin=row[4],
                    destination=row[5], category=row[6], username=row[7],
                    size_bytes=row[8], file_hash=row[9]
                ))
            return records
    
    def get_total_files_organized(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM history')
            return cursor.fetchone()[0]

    def get_total_size_freed(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(size_bytes) FROM history')
            result = cursor.fetchone()[0]
            return result if result else 0

    def undo_last_operation(self) -> HistoryRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM history ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                cursor.execute('DELETE FROM history WHERE id = ?', (row[0],))
                conn.commit()
                return HistoryRecord(*row)
            return None
