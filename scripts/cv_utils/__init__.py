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
from .project_paths import ProjectPaths, get_project_root
from .version_utils import (
    get_current_version,
    get_version_status,
    set_version,
    extract_name_from_personal_details,
    extract_personal_info,
)
from .error_handling import (
    CVScriptError,
    handle_error,
    require_file,
    require_directory,
    warn,
)

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
    'ProjectPaths',
    'get_project_root',
    'get_current_version',
    'get_version_status',
    'set_version',
    'extract_name_from_personal_details',
    'extract_personal_info',
    'CVScriptError',
    'handle_error',
    'require_file',
    'require_directory',
    'warn',
]
