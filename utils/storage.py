"""
Storage utilities for safe CRUD operations across app directories.

Provides a unified API to manage files and folders under logical roots:
@workflows, @tools, @templates, @temp, @sessions, @media, @logs, @exports, @cache, @output.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class StoragePaths:
    """Directory mappings for logical roots used across the app."""

    ROOT_MAP: Dict[str, Path] = {
        "@workflows": Path("output/workflows"),
        "@tools": Path("output/tools"),
        "@templates": Path("output/templates"),
        "@temp": Path("output/temp"),
        "@sessions": Path("output/sessions"),
        "@media": Path("output/media"),
        "@logs": Path("output/logs"),
        "@exports": Path("output/exports"),
        "@cache": Path("output/cache"),
        "@output": Path("output"),
    }

    @classmethod
    def resolve(cls, logical_root: str, *relative_parts: str) -> Path:
        base = cls.ROOT_MAP.get(logical_root)
        if base is None:
            raise ValueError(f"Unknown logical root: {logical_root}")
        candidate = base.joinpath(*relative_parts)
        # Prevent path traversal escaping the base
        base_abs = base.resolve()
        candidate_abs = candidate.resolve(strict=False)
        if not str(candidate_abs).startswith(str(base_abs)):
            raise ValueError("Path traversal attempt detected")
        return candidate


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_files(logical_root: str, pattern: str = "*") -> List[Path]:
    base = StoragePaths.resolve(logical_root)
    ensure_dir(base)
    return sorted([p for p in base.glob(pattern) if p.is_file()], key=lambda p: p.name)


def list_dirs(logical_root: str) -> List[Path]:
    base = StoragePaths.resolve(logical_root)
    ensure_dir(base)
    return sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name)


def read_text(logical_root: str, relative_path: str, default: Optional[str] = None) -> Optional[str]:
    path = StoragePaths.resolve(logical_root, relative_path)
    if not path.exists() or not path.is_file():
        return default
    return path.read_text(encoding="utf-8")


def write_text(logical_root: str, relative_path: str, content: str) -> bool:
    path = StoragePaths.resolve(logical_root, relative_path)
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def read_json(logical_root: str, relative_path: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    text = read_text(logical_root, relative_path)
    if text is None:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default


def write_json(logical_root: str, relative_path: str, data: Dict[str, Any]) -> bool:
    return write_text(logical_root, relative_path, json.dumps(data, indent=2, ensure_ascii=False))


def delete_path(logical_root: str, relative_path: str) -> bool:
    path = StoragePaths.resolve(logical_root, relative_path)
    if not path.exists():
        return True
    if path.is_dir():
        # Only allow deleting empty directories to avoid accidental data loss
        try:
            next(path.iterdir())
            return False
        except StopIteration:
            path.rmdir()
            return True
    else:
        path.unlink()
        return True


def ensure_empty_dir(logical_root: str, *relative_parts: str) -> Path:
    path = StoragePaths.resolve(logical_root, *relative_parts)
    ensure_dir(path)
    # Remove files inside (not subdirs) for a clean export/temp workflow
    for item in path.iterdir():
        if item.is_file():
            try:
                item.unlink()
            except Exception:
                pass
    return path


def exists(logical_root: str, relative_path: str) -> bool:
    path = StoragePaths.resolve(logical_root, relative_path)
    return path.exists()


def file_info(logical_root: str, relative_path: str) -> Optional[Dict[str, Any]]:
    path = StoragePaths.resolve(logical_root, relative_path)
    if not path.exists():
        return None
    return {
        "name": path.name,
        "size": path.stat().st_size,
        "path": str(path),
        "is_dir": path.is_dir(),
    }


