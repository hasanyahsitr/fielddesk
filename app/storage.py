"""Small portable-path and atomic-write helpers."""
import json
import os
from pathlib import Path
import uuid


def safe_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Hedef çantanın dışında.')
    return path


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def plain_child(path):
    return not path.is_symlink() and not getattr(os.path, 'isjunction', lambda p: False)(path)
