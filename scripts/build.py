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
    python scripts/build.py --skip-packages   # Skip automatic package check
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# Import the package manager (will be imported after we cd to project root)
PACKAGE_MANAGER_AVAILABLE = False
PackageManager = None


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


def check_and_install_packages():
    """Check for missing LaTeX packages and install them automatically"""
    if not PACKAGE_MANAGER_AVAILABLE:
        print_status("Package manager not available, skipping package check", 'warning')
        return True

    try:
        print_status("Checking LaTeX package dependencies...", 'info')
        manager = PackageManager()

        # Check packages and auto-install if needed
        success = manager.check_packages(auto_fix=True)

        if success:
            print_status("All package dependencies satisfied", 'success')
        else:
            print_status("Some packages could not be installed", 'warning')
            print("Build may fail if missing packages are required")

        return True  # Don't fail build, just warn

    except Exception as e:
        print_status(f"Error checking packages: {e}", 'warning')
        return True  # Don't fail build


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

    # Create a temporary build directory to keep root clean
    import shutil

    build_dir = Path.cwd() / '.build_temp'
    build_dir.mkdir(exist_ok=True)

    # Copy necessary files to build directory
    texmf_dir = Path.cwd() / 'texmf'
    project_root = Path.cwd()

    try:
        # Copy all required package files from texmf to build directory
        if texmf_dir.exists():
            for ext in ['*.sty', '*.cls', '*.def', '*.fd', '*.otf', '*.ttf', '*.pfb']:
                for source_file in texmf_dir.glob(ext):
                    target_file = build_dir / source_file.name
                    shutil.copy2(source_file, target_file)

        # Tectonic command with search path to find all project files
        # Output goes to build directory, keeping workspace clean
        subprocess.run(
            [
                'tectonic',
                '--keep-logs',
                '--keep-intermediates',
                '--outdir', str(build_dir),
                '-Z', f'search-path={project_root}',  # Search project root for inputs
                '-Z', f'search-path={build_dir}',      # Search build dir for packages
                str(tex_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Check if PDF was created in build directory
        pdf_path = build_dir / tex_path.with_suffix('.pdf').name
        if pdf_path.exists():
            size_kb = pdf_path.stat().st_size / 1024
            print_status(f"Built {output_name}.pdf ({size_kb:.1f} KB)", 'success')

            # Parse LaTeX log for warnings (log is in build directory)
            log_path = build_dir / tex_path.with_suffix('.log').name
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                    # Look for our custom warnings
                    import re
                    warnings = re.findall(r'Class resume-pipeline Warning: (.+)', log_content)
                    if warnings:
                        print_status("Content warnings found:", 'warning')
                        for warning in warnings:
                            print(f"  • {warning}")

            # Run post-build hook (copy PDF directly from build dir to output)
            try:
                version = get_current_version()
                doc_type = 'resume' if 'resume' in str(tex_path).lower() else 'coverletter'

                # Copy PDF directly from build directory to output directory
                # This avoids the intermediate step of moving to project root
                output_dir = Path.cwd() / '_output' / (version or 'default')
                output_dir.mkdir(parents=True, exist_ok=True)

                # Get full name from personal details for proper filename
                from copy_and_convert import extract_name_from_personal_details
                personal_details = Path.cwd() / "cv-personal-details.tex"
                full_name = extract_name_from_personal_details(personal_details)
                doc_type_name = "Resume" if doc_type == 'resume' else "Cover Letter"

                final_pdf = output_dir / f"{full_name} {doc_type_name}.pdf"
                shutil.copy2(pdf_path, final_pdf)
                print_status(f"Copied to: {final_pdf.relative_to(Path.cwd())}", 'success')

                # Run markdown conversion
                md_script = 'resume_to_markdown.py' if doc_type == 'resume' else 'cover_letter_to_markdown.py'
                result = subprocess.run(
                    ['python', f'scripts/{md_script}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print_status("Post-build hook completed", 'success')
                else:
                    print_status(f"Post-build hook warning: {result.stderr}", 'warning')
            except Exception as e:
                print_status(f"Post-build hook failed: {e}", 'warning')

            # Clean up build directory after successful build
            try:
                shutil.rmtree(build_dir)
            except Exception as e:
                print_status(f"Warning: Could not clean build directory: {e}", 'warning')

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

    finally:
        # Clean up build directory on failure
        if build_dir.exists():
            try:
                shutil.rmtree(build_dir)
            except Exception:
                pass  # Ignore cleanup errors


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
    parser.add_argument(
        '--skip-packages',
        action='store_true',
        help='Skip automatic package dependency check'
    )

    args = parser.parse_args()

    # Change to project root if running from scripts/
    if Path.cwd().name == 'scripts':
        os.chdir('..')

    # Import package manager after changing to project root
    global PACKAGE_MANAGER_AVAILABLE, PackageManager
    try:
        # Add scripts directory to path
        scripts_dir = Path.cwd() / 'scripts'
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        from latex_packages import PackageManager
        PACKAGE_MANAGER_AVAILABLE = True
    except ImportError as e:
        print_status(f"Package manager import failed: {e}", 'warning')
        PACKAGE_MANAGER_AVAILABLE = False

    print(f"\n{Colors.BOLD}Resume Build System{Colors.RESET}")
    print("=" * 50)

    # Check Tectonic installation
    if not check_tectonic():
        sys.exit(1)

    # Check and install LaTeX packages (unless skipped)
    if not args.skip_packages:
        check_and_install_packages()

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

    # Check if cover letter content exists
    version = get_current_version()
    cover_letter_exists = False
    if version:
        cover_letter_path = Path(f'_content/{version}/cover_letter.tex')
        cover_letter_exists = cover_letter_path.exists()

    # Skip cover letter if content doesn't exist (unless explicitly requested)
    if build_cover and not cover_letter_exists and not args.cover_letter:
        print_status(f"Skipping cover letter (no content found in _content/{version}/)", 'info')
        build_cover = False

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
