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

# Add scripts directory to path for cv_utils import
sys.path.insert(0, str(Path(__file__).parent))
from cv_utils import (  # noqa: E402
    Colors,
    ProjectPaths,
    get_version_status,
    set_version as set_cv_version,
    require_directory,
)


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


def set_version(version: str, paths: ProjectPaths) -> None:
    """Set the CV version in cv-version.tex."""
    version_path = paths.version_dir(version)

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

    # Set version using utility function
    set_cv_version(version, paths.version_file)
    print(f"{Colors.GREEN}✓ CV version set to: {version}{Colors.RESET}")

    if version_path.exists():
        status, color = get_version_status(version_path)
        print(f"{color}  Status: {status.strip()}{Colors.RESET}")


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

    # Initialize project paths
    paths = ProjectPaths()

    # Ensure _content directory exists
    require_directory(
        paths.content_dir,
        f"_content/ directory not found at {paths.content_dir}"
    )

    # List versions
    if args.list:
        list_versions(paths.content_dir)
        sys.exit(0)

    # Set version
    if not args.version:
        print(f"{Colors.RED}Error: Version parameter is required.{Colors.RESET}")
        print(f"{Colors.YELLOW}Usage: python set_version.py <version-name>{Colors.RESET}")
        print(f"{Colors.YELLOW}   or: python set_version.py --list{Colors.RESET}")
        sys.exit(1)

    set_version(args.version, paths)


if __name__ == '__main__':
    main()
