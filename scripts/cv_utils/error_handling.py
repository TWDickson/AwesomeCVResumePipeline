"""Error handling utilities for CV scripts."""

import sys
from pathlib import Path
from typing import NoReturn, Optional
from .console import print_status


class CVScriptError(Exception):
    """Base exception for CV script errors."""
    pass


class FileNotFoundError(CVScriptError):
    """Raised when a required file is not found."""
    pass


class VersionNotFoundError(CVScriptError):
    """Raised when a CV version is not found."""
    pass


class ValidationError(CVScriptError):
    """Raised when validation fails."""
    pass


def handle_error(message: str, exit_code: int = 1) -> NoReturn:
    """
    Print error message and exit.

    Args:
        message: Error message to display
        exit_code: Exit code (default: 1)
    """
    print_status(message, 'error')
    sys.exit(exit_code)


def require_file(file_path: Path, error_message: Optional[str] = None) -> None:
    """
    Ensure a file exists, exit with error if not.

    Args:
        file_path: Path to check
        error_message: Custom error message (optional)
    """
    if not file_path.exists():
        msg = error_message or f"Required file not found: {file_path}"
        handle_error(msg)


def require_directory(dir_path: Path, error_message: Optional[str] = None) -> None:
    """
    Ensure a directory exists, exit with error if not.

    Args:
        dir_path: Path to check
        error_message: Custom error message (optional)
    """
    if not dir_path.exists() or not dir_path.is_dir():
        msg = error_message or f"Required directory not found: {dir_path}"
        handle_error(msg)


def warn(message: str) -> None:
    """
    Print warning message without exiting.

    Args:
        message: Warning message to display
    """
    print_status(message, 'warning')
