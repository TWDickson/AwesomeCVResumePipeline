"""CV utilities package for shared functionality across CV scripts."""

from .regex_parsing import clean_latex_text, normalize_company, normalize_dates
from .file_io import (
    read_text_file,
    write_text_file,
    read_text_file_safe,
    file_exists,
    ensure_dir_exists,
    get_file_content_or_none,
)
from .console import Colors, print_status

__all__ = [
    'clean_latex_text',
    'normalize_company',
    'normalize_dates',
    'read_text_file',
    'write_text_file',
    'read_text_file_safe',
    'file_exists',
    'ensure_dir_exists',
    'get_file_content_or_none',
    'Colors',
    'print_status',
]
