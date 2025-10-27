#!/usr/bin/env python3
"""
CV Version Manager
Sets the CV version for resume and cover letter generation.

Usage:
    python set_version.py <version-name>
    python set_version.py --list
    python set_version.py -l

The version must match a folder name in the _content/ directory.
"""

import sys
import argparse
from pathlib import Path
from typing import Tuple

# Add scripts directory to path for cv_utils import
sys.path.insert(0, str(Path(__file__).parent))
from cv_utils import Colors


def get_version_status(version_dir: Path) -> Tuple[str, str]:
    """
    Check version folder completeness and return status indicator and color.

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


def list_versions(content_path: Path) -> None:
    """List all available CV versions from _content/ directory."""
    print(f"\n{Colors.CYAN}Available CV versions:{Colors.RESET}")

    versions = sorted([
        d for d in content_path.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ], key=lambda x: x.name)

    if not versions:
        print(f"{Colors.YELLOW}  No versions found in _content/{Colors.RESET}")
        return

    for version_dir in versions:
        status, color = get_version_status(version_dir)
        print(f"  {color}- {version_dir.name}{status}{Colors.RESET}")

    print()


def set_version(version: str, content_path: Path, version_file: Path) -> None:
    """Set the CV version in cv-version.tex."""
    version_path = content_path / version

    # Check if version folder exists
    if not version_path.exists():
        print(f"{Colors.YELLOW}Warning: Version folder '{version}' does not exist in _content/{Colors.RESET}")
        print(f"{Colors.YELLOW}The version will be set, but files will fall back to 'default' folder.{Colors.RESET}")

        try:
            response = input("Continue? (y/N): ").strip().lower()
            if response not in ('y', 'yes'):
                print(f"{Colors.RED}Cancelled.{Colors.RESET}")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.RED}Cancelled.{Colors.RESET}")
            sys.exit(1)

    # Generate cv-version.tex content
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

    # Write to file
    try:
        version_file.write_text(content, encoding='utf-8')
        print(f"{Colors.GREEN}✓ CV version set to: {version}{Colors.RESET}")

        if version_path.exists():
            status, color = get_version_status(version_path)
            print(f"{color}  Status: {status.strip()}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error writing to {version_file}: {e}{Colors.RESET}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Set CV version for resume and cover letter generation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generic
  %(prog)s --list
  %(prog)s -l
        """
    )

    parser.add_argument(
        'version',
        nargs='?',
        help='Version name (must match a folder in _content/)'
    )

    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List all available versions'
    )

    args = parser.parse_args()

    # Get paths
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    content_path = base_dir / "_content"
    version_file = base_dir / "cv-version.tex"

    # Ensure _content directory exists
    if not content_path.exists():
        print(f"{Colors.RED}Error: _content/ directory not found at {content_path}{Colors.RESET}")
        sys.exit(1)

    # List versions
    if args.list:
        list_versions(content_path)
        sys.exit(0)

    # Set version
    if not args.version:
        print(f"{Colors.RED}Error: Version parameter is required.{Colors.RESET}")
        print(f"{Colors.YELLOW}Usage: python set_version.py <version-name>{Colors.RESET}")
        print(f"{Colors.YELLOW}   or: python set_version.py --list{Colors.RESET}")
        sys.exit(1)

    set_version(args.version, content_path, version_file)


if __name__ == '__main__':
    main()
