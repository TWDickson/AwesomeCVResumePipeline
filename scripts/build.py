#!/usr/bin/env python3
"""
Build script for resume and cover letter using Tectonic.

Tectonic is a modern, self-contained TeX engine that handles dependencies automatically.
Install: https://tectonic-typesetting.github.io/
  - macOS: brew install tectonic
  - Windows: scoop install tectonic
  - Linux: See installation docs

Usage:
    python scripts/build.py                    # Build both resume and cover letter
    python scripts/build.py --resume          # Build resume only
    python scripts/build.py --cover-letter    # Build cover letter only
    python scripts/build.py --check           # Check if Tectonic is installed
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_status(message, status='info'):
    """Print colored status messages"""
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


def check_tectonic():
    """Check if Tectonic is installed and accessible"""
    try:
        result = subprocess.run(
            ['tectonic', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_status(f"Tectonic found: {version}", 'success')
        return True
    except FileNotFoundError:
        print_status("Tectonic not found!", 'error')
        print("\nPlease install Tectonic:")
        print("  macOS:    brew install tectonic")
        print("  Windows:  Download from https://github.com/tectonic-typesetting/tectonic/releases")
        print("  Linux:    https://tectonic-typesetting.github.io/install.html")
        return False
    except subprocess.CalledProcessError:
        print_status("Error running Tectonic", 'error')
        return False


def get_current_version():
    """Read the current version from cv-version.tex"""
    version_file = Path('cv-version.tex')
    if not version_file.exists():
        print_status("cv-version.tex not found!", 'error')
        return None

    content = version_file.read_text()
    # Extract version from \newcommand{\OutputVersion}{version_name}
    for line in content.split('\n'):
        if '\\newcommand{\\OutputVersion}' in line:
            # Extract content between braces
            start = line.find('{', line.find('\\OutputVersion')) + 1
            end = line.find('}', start)
            version = line[start:end]
            return version

    print_status("Could not parse version from cv-version.tex", 'error')
    return None


def check_version_content(version):
    """Check if version content directory exists"""
    if not version:
        return False

    content_dir = Path(f'_content/{version}')
    if not content_dir.exists():
        print_status(f"Content directory not found: {content_dir}", 'warning')
        print(f"  Expected: _content/{version}/")
        print(f"  Tip: Copy _content/_template/ to _content/{version}/ and fill it out")
        return False

    # Check for at least one .tex file
    tex_files = list(content_dir.glob('*.tex'))
    if not tex_files:
        print_status(f"No .tex files found in {content_dir}", 'warning')
        return False

    print_status(f"Using content version: {version}", 'info')
    return True


def build_document(tex_file, output_name=None):
    """Build a LaTeX document using Tectonic"""
    tex_path = Path(tex_file)
    if not tex_path.exists():
        print_status(f"File not found: {tex_file}", 'error')
        return False

    if output_name is None:
        output_name = tex_path.stem

    print_status(f"Building {output_name}...", 'info')

    try:
        # Tectonic command with shell escape for Python scripts
        result = subprocess.run(
            [
                'tectonic',
                '--keep-logs',
                '--keep-intermediates',
                str(tex_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Check if PDF was created
        pdf_path = tex_path.with_suffix('.pdf')
        if pdf_path.exists():
            size_kb = pdf_path.stat().st_size / 1024
            print_status(f"Built {output_name}.pdf ({size_kb:.1f} KB)", 'success')
            return True
        else:
            print_status(f"PDF not created for {output_name}", 'error')
            return False

    except subprocess.CalledProcessError as e:
        print_status(f"Build failed for {output_name}", 'error')
        print("\nError output:")
        print(e.stderr)

        # Check for common issues
        if "Section" in e.stderr and "not found" in e.stderr:
            print("\n" + Colors.YELLOW + "Hint:" + Colors.RESET)
            print("  Missing section files. Make sure you've created content in:")
            version = get_current_version()
            if version:
                print(f"  _content/{version}/")

        return False


def main():
    parser = argparse.ArgumentParser(
        description='Build resume and cover letter using Tectonic',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Build resume only'
    )
    parser.add_argument(
        '--cover-letter',
        action='store_true',
        help='Build cover letter only'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if Tectonic is installed'
    )

    args = parser.parse_args()

    # Change to project root if running from scripts/
    if Path.cwd().name == 'scripts':
        os.chdir('..')

    print(f"\n{Colors.BOLD}Resume Build System{Colors.RESET}")
    print("=" * 50)

    # Check Tectonic installation
    if not check_tectonic():
        sys.exit(1)

    if args.check:
        print_status("Tectonic is ready to use!", 'success')
        sys.exit(0)

    # Check version and content
    version = get_current_version()
    if version:
        check_version_content(version)

    print()

    # Determine what to build
    build_resume = args.resume or not args.cover_letter
    build_cover = args.cover_letter or not args.resume

    success = True

    if build_resume:
        if not build_document('cv-resume.tex', 'Resume'):
            success = False

    if build_cover:
        if not build_document('cv-coverletter.tex', 'Cover Letter'):
            success = False

    print("\n" + "=" * 50)
    if success:
        print_status("Build completed successfully!", 'success')
        sys.exit(0)
    else:
        print_status("Build completed with errors", 'error')
        sys.exit(1)


if __name__ == '__main__':
    main()
