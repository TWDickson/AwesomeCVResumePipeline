"""File I/O utilities for CV scripts."""

from pathlib import Path
from typing import Union, Optional


def read_text_file(file_path: Union[str, Path]) -> str:
    """
    Read a text file with UTF-8 encoding.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(file_path: Union[str, Path], content: str) -> None:
    """
    Write content to a text file with UTF-8 encoding.

    Args:
        file_path: Path to the file to write
        content: Content to write
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_text_file_safe(file_path: Union[str, Path], default: str = "") -> str:
    """
    Read a text file with UTF-8 encoding, returning default if file doesn't exist.

    Args:
        file_path: Path to the file to read
        default: Default value to return if file doesn't exist

    Returns:
        File content as string, or default if file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        return default
    return read_text_file(path)


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to check

    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).exists()


def ensure_dir_exists(dir_path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if needed.

    Args:
        dir_path: Directory path to ensure exists

    Returns:
        Path object for the directory
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_content_or_none(file_path: Union[str, Path]) -> Optional[str]:
    """
    Read file content or return None if file doesn't exist.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string, or None if file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        return None
    return read_text_file(path)
