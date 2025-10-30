"""CV version management utilities."""

import re
from pathlib import Path
from typing import Tuple, Optional, Dict
from .console import Colors


def get_current_version(version_file: Path) -> Optional[str]:
    """
    Read the current version from cv-version.tex.

    Args:
        version_file: Path to cv-version.tex

    Returns:
        Version name, or None if not found
    """
    if not version_file.exists():
        return None

    content = version_file.read_text(encoding='utf-8')

    # Extract version from \newcommand{\OutputVersion}{version_name}
    for line in content.split('\n'):
        if '\\newcommand{\\OutputVersion}' in line:
            # Extract content between braces
            start = line.find('{', line.find('\\OutputVersion')) + 1
            end = line.find('}', start)
            if start > 0 and end > start:
                return line[start:end]

    return None


def get_version_status(version_dir: Path) -> Tuple[str, str]:
    """
    Check version folder completeness and return status indicator and color.

    Args:
        version_dir: Path to version directory

    Returns:
        Tuple of (status_text, color_code)
    """
    has_tagline = (version_dir / "tagline.tex").exists()
    has_experience = (version_dir / "experience.tex").exists()
    has_cover_letter = (version_dir / "cover_letter.tex").exists()

    if has_tagline and has_experience and has_cover_letter:
        return " [Complete]", Colors.GREEN
    elif has_tagline and has_experience:
        return " [Resume Ready]", Colors.CYAN
    elif has_tagline or has_experience or has_cover_letter:
        return " [Partial]", Colors.YELLOW
    else:
        return "", Colors.RESET


def set_version(version: str, version_file: Path) -> None:
    """
    Set the CV version in cv-version.tex.

    Args:
        version: Version name to set
        version_file: Path to cv-version.tex
    """
    content = f"""%-------------------------------------------------------------------------------
% Version Configuration
%-------------------------------------------------------------------------------
% This file defines the output version for both resume and cover letter.
% The version name should match a folder in the _content/ directory.
%
% Usage:
%   1. Manually edit this file and change the version name
%   2. Use VS Code task: "Set CV Version" (Ctrl+Shift+P -> Tasks: Run Task)
%   3. Use Python script: python scripts/set_version.py <version-name>
%   4. List available versions: python scripts/set_version.py --list
%
% If a file is not found in the specified version folder, it will
% automatically fall back to the 'default' folder.
%-------------------------------------------------------------------------------

\\newcommand{{\\OutputVersion}}{{{version}}}
"""
    version_file.write_text(content, encoding='utf-8')


def extract_name_from_personal_details(personal_details_path: Path) -> str:
    """
    Extract the full name from cv-personal-details.tex.

    Args:
        personal_details_path: Path to cv-personal-details.tex

    Returns:
        Full name in format "FirstName LastName", or "CV" as fallback
    """
    try:
        content = personal_details_path.read_text(encoding='utf-8')

        # Look for \name{First}{Last}
        name_match = re.search(r'\\name\{([^}]+)\}\{([^}]+)\}', content)

        if name_match:
            first_name = name_match.group(1).strip()
            last_name = name_match.group(2).strip()
            return f"{first_name} {last_name}"

        # Fallback
        return "CV"
    except Exception:
        return "CV"


def extract_personal_info(personal_details_path: Path) -> Dict[str, str]:
    """
    Extract comprehensive personal information from cv-personal-details.tex.

    Args:
        personal_details_path: Path to cv-personal-details.tex

    Returns:
        Dictionary with personal info fields (name, mobile, email, homepage, github, linkedin)
    """
    try:
        content = personal_details_path.read_text(encoding='utf-8')
    except Exception:
        return {}

    info = {}

    # Extract name
    name_match = re.search(r'\\name\{([^}]+)\}\{([^}]+)\}', content)
    if name_match:
        info['name'] = f"{name_match.group(1).strip()} {name_match.group(2).strip()}"

    # Extract contact details
    mobile_match = re.search(r'\\mobile\{[^}]+\}\{([^}]+)\}', content)
    if mobile_match:
        info['mobile'] = mobile_match.group(1).strip()

    email_match = re.search(r'\\email\{([^}]+)\}', content)
    if email_match:
        info['email'] = email_match.group(1).strip()

    homepage_match = re.search(r'\\homepage\{([^}]+)\}', content)
    if homepage_match:
        info['homepage'] = homepage_match.group(1).strip()

    github_match = re.search(r'\\github\{([^}]+)\}', content)
    if github_match:
        info['github'] = github_match.group(1).strip()

    linkedin_match = re.search(r'\\linkedin\{([^}]+)\}', content)
    if linkedin_match:
        info['linkedin'] = linkedin_match.group(1).strip()

    return info
