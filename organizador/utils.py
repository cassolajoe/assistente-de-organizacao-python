import hashlib
import os
import shutil
import logging
from pathlib import Path
from typing import Optional

def get_file_hash(filepath: str | Path, block_size: int = 65536) -> Optional[str]:
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                hasher.update(block)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Erro ao calcular hash de {filepath}: {e}")
        return None

def format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def is_file_in_use(filepath: str | Path) -> bool:
    try:
        with open(filepath, 'a'):
            pass
        return False
    except IOError:
        return True
    except Exception:
        return True

def ensure_dir(dir_path: str | Path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def safe_move(src: str | Path, dst_dir: str | Path, fallback_ext: str = "") -> str:
    src_path = Path(src)
    dst_dir_path = Path(dst_dir)
    ensure_dir(dst_dir_path)

    filename = src_path.name
    if fallback_ext and not src_path.suffix:
        filename = f"{src_path.stem}.{fallback_ext.strip('.')}"
    
    dst_path = dst_dir_path / filename
    
    counter = 1
    while dst_path.exists():
        new_name = f"{src_path.stem} ({counter}){dst_path.suffix}"
        dst_path = dst_dir_path / new_name
        counter += 1

    shutil.move(str(src_path), str(dst_path))
    return str(dst_path)
