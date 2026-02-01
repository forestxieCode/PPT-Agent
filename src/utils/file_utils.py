"""
File utility functions
"""

import json
from pathlib import Path
from typing import Any, Dict

from src.exceptions import TemplateNotFoundError, InvalidTemplateError


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        TemplateNotFoundError: File not found
        InvalidTemplateError: Invalid JSON format
    """
    if not file_path.exists():
        raise TemplateNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise InvalidTemplateError(f"Invalid JSON format in {file_path}: {e}")


def save_json(data: Dict[str, Any], file_path: Path, indent: int = 2) -> None:
    """
    Save data to JSON file

    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation (default: 2)
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def ensure_dir(dir_path: Path) -> None:
    """
    Ensure directory exists

    Args:
        dir_path: Directory path
    """
    dir_path.mkdir(parents=True, exist_ok=True)
