#!/usr/bin/env python3
"""
Resume Pipeline - Interactive CLI Manager

A unified command-line interface for managing your resume pipeline.
Provides both interactive menus and command-line flags for automation.

Usage:
    python pipeline.py                    # Interactive mode
    python pipeline.py --help             # Show all options
    python pipeline.py --new-version      # Create new version interactively
    python pipeline.py --set-version      # Select version interactively
    python pipeline.py --build            # Build current version
    python pipeline.py --validate         # Validate current version
    python pipeline.py --export           # Export current version to markdown
    python pipeline.py --clean            # Clean build artifacts
    python pipeline.py --duplicate src    # Duplicate a version
    python pipeline.py --delete old       # Delete a version
    python pipeline.py --list             # List all versions
    python pipeline.py --refresh-library  # Regenerate CV library JSON
    python pipeline.py --status           # Show pipeline status
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List
import shutil
import subprocess
import json
import re
import os

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from cv_parser import CVParser  # noqa: E402
from generate_tasks import generate_tasks_json  # noqa: E402
from cv_utils import Colors  # noqa: E402


# Helper functions to work with existing scripts
def get_available_versions() -> List[str]:
    """Get list of available versions from _content/."""
    content_path = Path.cwd() / '_content'
    if not content_path.exists():
        return []

    versions = sorted([
        d.name for d in content_path.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ])
    return versions


def get_current_version() -> str:
    """Get the current version from cv-version.tex."""
    version_file = Path.cwd() / 'cv-version.tex'

    if not version_file.exists():
        return 'default'

    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract version from \newcommand{\OutputVersion}{version_name}
            match = re.search(r'\\newcommand\{\\OutputVersion\}\{([^}]+)\}', content)
            if match:
                return match.group(1)
    except Exception:
        pass

    return 'default'


def get_version_status(version: str) -> str:
    """Get status indicator for a version."""
    content_path = Path.cwd() / '_content'
    version_dir = content_path / version

    if not version_dir.exists():
        return '[Not Found]'

    has_tagline = (version_dir / "tagline.tex").exists()
    has_experience = (version_dir / "experience.tex").exists()
    has_cover_letter = (version_dir / "cover_letter.tex").exists()

    if has_tagline and has_experience and has_cover_letter:
        return '[Complete]'
    elif has_tagline and has_experience:
        return '[Resume Ready]'
    elif has_tagline or has_experience or has_cover_letter:
        return '[Partial]'
    else:
        return '[Empty]'


def update_version(version: str) -> None:
    """Update the version in cv-version.tex."""
    version_file = Path.cwd() / 'cv-version.tex'

    if not version_file.exists():
        # If file doesn't exist, create with minimal content
        content = f"\\newcommand{{\\OutputVersion}}{{{version}}}\n"
        version_file.write_text(content, encoding='utf-8')
        return

    # Read all lines and replace only the \newcommand line
    lines = version_file.read_text(encoding='utf-8').splitlines()
    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith('\\newcommand{\\OutputVersion}'):
            new_lines.append(f"\\newcommand{{\\OutputVersion}}{{{version}}}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        # If the command was not found, append it at the end
        new_lines.append(f"\\newcommand{{\\OutputVersion}}{{{version}}}")
    version_file.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def create_new_version(version_name: Optional[str] = None) -> bool:
    """Create a new resume version from template.

    Args:
        version_name: Optional name for the version. If None, prompts user.

    Returns:
        True if successful, False otherwise.
    """
    print_header("Create New Resume Version")

    base_path = Path.cwd()
    content_dir = base_path / '_content'
    template_dir = content_dir / '_template'

    if not template_dir.exists():
        print_error("Template directory not found at _content/_template/")
        return False


    # Get version name
    if version_name is None:
        print_info("Enter a name for the new version (e.g., 'acme_corp', 'senior_engineer')")
        print_info("Use lowercase with underscores, no spaces")
        version_name = input(f"{Colors.BOLD}Version name: {Colors.ENDC}").strip()

    if not version_name:
        print_error("Version name cannot be empty")
        return False

    # Normalize version name
    normalized = re.sub(r'[^a-zA-Z0-9_-]', '', version_name.replace(' ', '_').lower())
    if version_name != normalized:
        print_warning(f"Version name '{version_name}' is not in the recommended format.")
        print_info(f"Suggested: {Colors.CYAN}{normalized}{Colors.ENDC}")
        action = input(f"Use suggested name? (Y/edit/cancel): {Colors.ENDC}").strip().lower()
        if action == 'y' or action == 'yes' or action == '':
            version_name = normalized
        elif action == 'edit':
            version_name = input(f"{Colors.BOLD}Edit version name: {Colors.ENDC}").strip()
            if not version_name:
                print_error("Version name cannot be empty")
                return False
            version_name = re.sub(r'[^a-zA-Z0-9_-]', '', version_name.replace(' ', '_').lower())
        else:
            print_info("Cancelled")
            return False

    # Validate version name
    if not version_name.replace('_', '').replace('-', '').isalnum():
        print_error("Version name must contain only letters, numbers, underscores, and hyphens")
        return False

    new_version_dir = content_dir / version_name

    # Check if version already exists
    if new_version_dir.exists():
        print_error(f"Version '{version_name}' already exists!")
        return False

    # Show preview
    print(f"\n{Colors.BOLD}Preview:{Colors.ENDC}")
    print(f"  Name: {Colors.CYAN}{version_name}{Colors.ENDC}")
    print(f"  Path: {Colors.CYAN}{new_version_dir.relative_to(base_path)}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Files to be created:{Colors.ENDC}")

    template_files = sorted([f.name for f in template_dir.glob('*.tex')])
    for file in template_files:
        print(f"  - {file}")

    # Confirm
    confirm = input(f"\n{Colors.BOLD}Create this version? (y/N): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print_info("Cancelled")
        return False

    # Copy template, skipping .gitignore
    try:
        new_version_dir.mkdir(parents=True, exist_ok=False)
        for item in template_dir.iterdir():
            if item.name == '.gitignore':
                continue
            if item.is_file():
                shutil.copy2(item, new_version_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, new_version_dir / item.name)
        print_success(f"Created new version: {version_name}")

        # Ask if user wants to switch to it
        switch = input(f"\n{Colors.BOLD}Switch to this version now? (Y/n): {Colors.ENDC}").strip().lower()
        if switch != 'n':
            update_version(version_name)
            print_success(f"Switched to version: {version_name}")

        # Suggest next steps
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. Edit files in {Colors.CYAN}_content/{version_name}/{Colors.ENDC}")
        print("  2. Customize the content for your specific use case")
        print(f"  3. Run {Colors.CYAN}python pipeline.py --build{Colors.ENDC} to generate PDF")

        return True

    except Exception as e:
        print_error(f"Failed to create version: {e}")
        return False


def select_version_interactive() -> bool:
    """Interactive version selection with status indicators.

    Returns:
        True if version was changed, False otherwise.
    """
    clear_screen()
    print(f"\n  {Colors.DIM}Resume Pipeline{Colors.ENDC} {Colors.CYAN}›{Colors.ENDC} {Colors.BOLD}Switch Version{Colors.ENDC}\n")  # noqa e501

    versions = get_available_versions()
    current = get_current_version()

    if not versions:
        print_error("No versions found in _content/")
        return False

    print(f"  {Colors.DIM}Current:{Colors.ENDC} {Colors.CYAN}{Colors.BOLD}{current}{Colors.ENDC}")
    print(f"  {Colors.DIM}Legend: {Colors.GREEN}●{Colors.ENDC} Complete  {Colors.CYAN}●{Colors.ENDC} Resume Ready  {Colors.YELLOW}●{Colors.ENDC} Partial{Colors.ENDC}\n") # noqa e501

    # Display versions with status
    for i, version in enumerate(versions, 1):
        status = get_version_status(version)
        current_marker = f" {Colors.DIM}(current){Colors.ENDC}" if version == current else ""

        # Color-code status
        if status == '[Complete]':
            status_colored = f"{Colors.GREEN}●{Colors.ENDC}"
        elif status == '[Resume Ready]':
            status_colored = f"{Colors.CYAN}●{Colors.ENDC}"
        else:
            status_colored = f"{Colors.YELLOW}●{Colors.ENDC}"

        # Truncate long names
        display_name = version[:45] + "..." if len(version) > 48 else version
        print(f"  {Colors.BOLD}{i:2}{Colors.ENDC} {status_colored} {display_name}{current_marker}")

    print(f"\n  {Colors.DIM} 0 › Cancel{Colors.ENDC}")

    # Get selection
    try:
        choice = input(f"\n{Colors.BOLD}›{Colors.ENDC} ").strip()

        if choice == '0' or choice == '':
            print_info("Cancelled")
            return False

        choice_num = int(choice)
        if 1 <= choice_num <= len(versions):
            selected = versions[choice_num - 1]

            if selected == current:
                print_info(f"Already using version: {selected}")
                return False

            update_version(selected)
            print_success(f"Switched to version: {selected}")
            return True
        else:
            print_error("Invalid selection")
            return False

    except ValueError:
        print_error("Invalid input")
        return False


def list_versions() -> None:
    """List all available versions with their status."""
    print_header("Available Resume Versions")

    versions = get_available_versions()
    current = get_current_version()

    if not versions:
        print_error("No versions found in _content/")
        return

    print(f"Current version: {Colors.CYAN}{Colors.BOLD}{current}{Colors.ENDC}\n")

    for version in versions:
        status = get_version_status(version)
        current_marker = " ← current" if version == current else ""

        # Color-code status
        if status == '[Complete]':
            status_colored = f"{Colors.GREEN}{status}{Colors.ENDC}"
        elif status == '[Resume Ready]':
            status_colored = f"{Colors.CYAN}{status}{Colors.ENDC}"
        else:
            status_colored = f"{Colors.YELLOW}{status}{Colors.ENDC}"

        print(f"  {Colors.BOLD}{version}{Colors.ENDC} {status_colored}{current_marker}")


def build_resume(version: Optional[str] = None) -> bool:
    """Build resume PDF(s) for a version.

    Args:
        version: Version to build. If None, uses current version.

    Returns:
        True if successful, False otherwise.
    """
    if version is None:
        version = get_current_version()

    print_header(f"Building Resume & Cover Letter: {version}")

    try:
        # Run build script for both resume and cover letter
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'build.py')],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        # Check for cover letter section
        content_dir = Path.cwd() / '_content' / version
        cover_letter_path = content_dir / 'cover_letter.tex'
        if not cover_letter_path.exists():
            print_warning("No cover letter section found for this version. Skipping cover letter build.")

        if result.returncode == 0:
            print_success(f"Resume and cover letter build complete for version: {version}")
            return True
        else:
            print_error("Build failed")
            if result.stderr:
                print(result.stderr)
            return False

    except Exception as e:
        print_error(f"Build error: {e}")
        return False


def refresh_library() -> bool:
    """Regenerate the CV library JSON files.

    Returns:
        True if successful, False otherwise.
    """
    print_header("Refresh CV Library")

    print_info("Parsing all CV versions...")

    try:
        parser = CVParser()

        print_info("Parsing CV files...")
        parser.parse_all_cvs()

        print_info("Merging jobs by company/year...")
        parser.merge_jobs()

        print_info("Exporting to JSON...")
        parser.export_to_json()

        print_success("CV library refreshed successfully!")
        return True

    except Exception as e:
        print_error(f"Failed to refresh library: {e}")
        return False


def refresh_vscode_tasks() -> bool:
    """Regenerate VS Code tasks.json.

    Returns:
        True if successful, False otherwise.
    """
    print_header("Refresh VS Code Tasks")

    try:
        # Get available versions
        versions = get_available_versions()

        # Generate tasks JSON structure
        tasks_dict = generate_tasks_json(versions)

        # Write to .vscode/tasks.json
        vscode_dir = Path.cwd() / '.vscode'
        vscode_dir.mkdir(exist_ok=True)

        tasks_file = vscode_dir / 'tasks.json'
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_dict, f, indent=4, ensure_ascii=False)

        print_success("VS Code tasks updated successfully!")
        print_info(f"Updated {tasks_file.relative_to(Path.cwd())} with {len(versions)} versions")
        return True
    except Exception as e:
        print_error(f"Failed to update tasks: {e}")
        return False


def clean_build_artifacts(clean_all: bool = False) -> bool:
    """Clean LaTeX build artifacts and temporary files.

    Args:
        clean_all: If True, also removes PDFs and output directories

    Returns:
        True if successful, False otherwise.
    """
    print_header("Clean Build Artifacts" if not clean_all else "Deep Clean")

    base_path = Path.cwd()

    # Patterns to clean
    patterns = [
        '*.aux', '*.log', '*.out', '*.toc', '*.fdb_latexmk',
        '*.fls', '*.synctex.gz', '*.bbl', '*.blg', '*.bcf',
        '*.run.xml', '*.idx', '*.ilg', '*.ind', '*.lof',
        '*.lot', '*.nav', '*.snm', '*.vrb', '*.xdv'
    ]

    # Add PDFs if doing full clean
    if clean_all:
        patterns.extend(['cv-*.pdf', '*.pdf'])

    files_removed = []

    print_info("Searching for build artifacts...")

    for pattern in patterns:
        for file in base_path.glob(pattern):
            try:
                file.unlink()
                files_removed.append(file.name)
            except Exception as e:
                print_warning(f"Could not remove {file.name}: {e}")

    # Clean __pycache__ directories
    for pycache in base_path.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache)
            files_removed.append(str(pycache.relative_to(base_path)))
        except Exception as e:
            print_warning(f"Could not remove {pycache}: {e}")

    # Clean output directory if doing full clean
    if clean_all:
        version = get_current_version()
        if version:
            output_dir = base_path / '_output' / version
            if output_dir.exists():
                print_info(f"Removing output directory: {output_dir.relative_to(base_path)}")
                try:
                    shutil.rmtree(output_dir)
                    files_removed.append(f"_output/{version}/")
                    print_success("Removed output directory")
                except Exception as e:
                    print_warning(f"Could not remove output directory: {e}")

    # Clean symlinked package files in project root
    texmf_dir = base_path / 'texmf'
    if texmf_dir.exists():
        print_info("Cleaning symlinked package files...")
        for ext in ['*.sty', '*.cls', '*.def', '*.fd', '*.otf', '*.ttf', '*.pfb']:
            for file in base_path.glob(ext):
                # Check if it's a symlink or if the same file exists in texmf
                if file.is_symlink() or (texmf_dir / file.name).exists():
                    try:
                        file.unlink()
                        files_removed.append(file.name)
                    except Exception as e:
                        print_warning(f"Could not remove {file.name}: {e}")

    if files_removed:
        print_success(f"Removed {len(files_removed)} artifact(s):")
        for file in sorted(files_removed)[:10]:  # Show first 10
            print(f"  - {file}")
        if len(files_removed) > 10:
            print(f"  ... and {len(files_removed) - 10} more")
        return True
    else:
        print_info("No artifacts found to clean")
        return True


def validate_version(version: Optional[str] = None) -> bool:
    """Validate LaTeX files for common errors and control characters.

    Args:
        version: Version to validate. If None, validates current version.

    Returns:
        True if validation passed, False otherwise.
    """
    if version is None:
        version = get_current_version()

    print_header(f"Validate Version: {version}")

    content_dir = Path.cwd() / '_content' / version

    if not content_dir.exists():
        print_error(f"Version directory not found: {version}")
        return False

    tex_files = list(content_dir.glob('*.tex'))

    if not tex_files:
        print_warning(f"No .tex files found in {version}")
        return True

    errors_found = False
    warnings_found = False

    for tex_file in sorted(tex_files):
        print(f"\n{Colors.BOLD}Checking {tex_file.name}:{Colors.ENDC}")

        try:
            content = tex_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print_error("  ✗ File encoding error - not valid UTF-8")
            errors_found = True
            continue

        file_errors = []
        file_warnings = []

        # Check for control characters (except newline, tab, carriage return)
        for i, line in enumerate(content.split('\n'), 1):
            for j, char in enumerate(line, 1):
                if ord(char) < 32 and char not in '\t\r':
                    file_errors.append(f"    Line {i}, col {j}: Control character (ASCII {ord(char)})")

        # Check for common LaTeX errors
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Unclosed braces (basic check)
            open_braces = line.count('{') - line.count('\\{')
            close_braces = line.count('}') - line.count('\\}')
            if open_braces != close_braces:
                file_warnings.append(f"    Line {i}: Mismatched braces (may be multi-line)")

            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                file_warnings.append(f"    Line {i}: Trailing whitespace")

            # Template placeholders still present
            if '[' in line and ']' in line:
                placeholders = re.findall(r'\[[A-Z][^\]]*\]', line)
                if placeholders:
                    file_warnings.append(f"    Line {i}: Template placeholder found: {placeholders[0]}")

            # Common typos
            if '\\begin{' in line:
                env_match = re.search(r'\\begin\{([^}]+)\}', line)
                if env_match:
                    env_name = env_match.group(1)
                    # Check if there's a matching \end
                    if f'\\end{{{env_name}}}' not in content:
                        file_warnings.append(f"    Line {i}: \\begin{{{env_name}}} may be missing \\end{{{env_name}}}")

        # Display results for this file
        if file_errors:
            print_error(f"  Found {len(file_errors)} error(s):")
            for error in file_errors[:5]:  # Show first 5
                print(error)
            if len(file_errors) > 5:
                print(f"    ... and {len(file_errors) - 5} more")
            errors_found = True

        if file_warnings:
            print_warning(f"  Found {len(file_warnings)} warning(s):")
            for warning in file_warnings[:5]:  # Show first 5
                print(warning)
            if len(file_warnings) > 5:
                print(f"    ... and {len(file_warnings) - 5} more")
            warnings_found = True

        if not file_errors and not file_warnings:
            print_success("  No issues found")

    # Summary
    print(f"\n{Colors.BOLD}Validation Summary:{Colors.ENDC}")
    if errors_found:
        print_error("Validation failed - errors found")
        return False
    elif warnings_found:
        print_warning("Validation passed with warnings")
        return True
    else:
        print_success("All files validated successfully!")
        return True


def export_to_markdown(version: Optional[str] = None) -> bool:
    """Export version to markdown format.

    Args:
        version: Version to export. If None, uses current version.

    Returns:
        True if successful, False otherwise.
    """
    if version is None:
        version = get_current_version()

    print_header(f"Export to Markdown: {version}")

    try:
        # Run resume_to_markdown
        print_info("Converting resume to markdown...")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'resume_to_markdown.py')],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print_error("Resume conversion failed")
            if result.stderr:
                print(result.stderr)
            return False

        print(result.stdout.strip())

        # Check for cover letter
        content_dir = Path.cwd() / '_content' / version
        if (content_dir / 'cover_letter.tex').exists():
            print_info("Converting cover letter to markdown...")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'cover_letter_to_markdown.py')],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print_warning("Cover letter conversion failed")
            else:
                print(result.stdout.strip())

        print_success("Markdown export complete!")

        output_dir = Path.cwd() / '_output' / version
        if output_dir.exists():
            md_files = list(output_dir.glob('*.md'))
            if md_files:
                print(f"\n{Colors.BOLD}Exported files:{Colors.ENDC}")
                for md_file in md_files:
                    print(f"  - {md_file.relative_to(Path.cwd())}")

        return True

    except Exception as e:
        print_error(f"Export failed: {e}")
        return False


def duplicate_version(source: str, dest: Optional[str] = None) -> bool:
    """Duplicate an existing version.

    Args:
        source: Source version name
        dest: Destination version name. If None, prompts user.

    Returns:
        True if successful, False otherwise.
    """
    print_header("Duplicate Version")

    content_dir = Path.cwd() / '_content'
    source_dir = content_dir / source

    # Check if source exists
    if not source_dir.exists():
        print_error(f"Source version '{source}' not found")
        return False

    # Get destination name
    if dest is None:
        print_info(f"Creating duplicate of: {Colors.CYAN}{source}{Colors.ENDC}")
        dest = input(f"{Colors.BOLD}New version name: {Colors.ENDC}").strip()

    if not dest:
        print_error("Destination name cannot be empty")
        return False

    # Validate destination name
    if not dest.replace('_', '').replace('-', '').isalnum():
        print_error("Version name must contain only letters, numbers, underscores, and hyphens")
        return False

    dest_dir = content_dir / dest

    # Check if destination exists
    if dest_dir.exists():
        print_error(f"Version '{dest}' already exists!")
        return False

    # Show preview
    print(f"\n{Colors.BOLD}Preview:{Colors.ENDC}")
    print(f"  Source: {Colors.CYAN}{source}{Colors.ENDC}")
    print(f"  Destination: {Colors.CYAN}{dest}{Colors.ENDC}")

    files = list(source_dir.glob('*.tex'))
    print(f"  Files to copy: {len(files)}")

    # Confirm
    confirm = input(f"\n{Colors.BOLD}Create duplicate? (y/N): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print_info("Cancelled")
        return False

    # Copy
    try:
        shutil.copytree(source_dir, dest_dir)
        print_success(f"Created duplicate: {dest}")

        # Ask if user wants to switch to it
        switch = input(f"\n{Colors.BOLD}Switch to this version now? (Y/n): {Colors.ENDC}").strip().lower()
        if switch != 'n':
            update_version(dest)
            print_success(f"Switched to version: {dest}")

        return True

    except Exception as e:
        print_error(f"Failed to duplicate: {e}")
        return False


def delete_version(version: str) -> bool:
    """Delete a version with confirmation.

    Args:
        version: Version name to delete

    Returns:
        True if successful, False otherwise.
    """
    print_header("Delete Version")

    content_dir = Path.cwd() / '_content'
    version_dir = content_dir / version

    # Check if version exists
    if not version_dir.exists():
        print_error(f"Version '{version}' not found")
        return False

    # Prevent deleting special directories
    if version.startswith('_'):
        print_error(f"Cannot delete special directory: {version}")
        return False

    # Check if it's the current version
    current = get_current_version()
    if version == current:
        print_warning(f"'{version}' is currently active!")

    # Show what will be deleted
    files = list(version_dir.glob('*.tex'))
    print(f"\n{Colors.BOLD}Version to delete:{Colors.ENDC}")
    print(f"  Name: {Colors.RED}{version}{Colors.ENDC}")
    print(f"  Path: {version_dir.relative_to(Path.cwd())}")
    print(f"  Files: {len(files)}")

    # Double confirmation
    print(f"\n{Colors.RED}{Colors.BOLD}WARNING: This action cannot be undone!{Colors.ENDC}")
    confirm1 = input(f"{Colors.BOLD}Type version name to confirm: {Colors.ENDC}").strip()

    if confirm1 != version:
        print_info("Cancelled - name didn't match")
        return False

    confirm2 = input(f"{Colors.BOLD}Are you absolutely sure? (yes/NO): {Colors.ENDC}").strip().lower()

    if confirm2 != 'yes':
        print_info("Cancelled")
        return False

    # Delete
    try:
        shutil.rmtree(version_dir)
        print_success(f"Deleted version: {version}")

        # Also delete output directory if it exists
        output_dir = Path.cwd() / '_output' / version
        if output_dir.exists():
            shutil.rmtree(output_dir)
            print_info("Deleted output directory")

        # If it was current, suggest switching
        if version == current:
            print_warning("Deleted the current version!")
            versions = get_available_versions()
            if versions:
                print_info(f"Available versions: {', '.join(versions[:3])}")
                switch = input(f"\n{Colors.BOLD}Switch to another version? (Y/n): {Colors.ENDC}").strip().lower()
                if switch != 'n':
                    select_version_interactive()

        return True

    except Exception as e:
        print_error(f"Failed to delete: {e}")
        return False


def show_status() -> None:
    """Show current pipeline status and information."""
    print_header("Resume Pipeline Status")

    current = get_current_version()
    versions = get_available_versions()
    status = get_version_status(current)

    # Current version info
    print(f"{Colors.BOLD}Current Version:{Colors.ENDC}")
    print(f"  Name: {Colors.CYAN}{current}{Colors.ENDC}")
    print(f"  Status: {status}")

    # Check for outputs
    output_dir = Path.cwd() / '_output' / current
    if output_dir.exists():
        pdfs = list(output_dir.glob('*.pdf'))
        if pdfs:
            print(f"\n{Colors.BOLD}Generated PDFs:{Colors.ENDC}")
            for pdf in pdfs:
                size_kb = pdf.stat().st_size / 1024
                print(f"  - {pdf.name} ({size_kb:.1f} KB)")

    # Version count
    print(f"\n{Colors.BOLD}Available Versions:{Colors.ENDC}")
    print(f"  Total: {len(versions)}")

    complete = sum(1 for v in versions if get_version_status(v) == '[Complete]')
    resume_ready = sum(1 for v in versions if get_version_status(v) == '[Resume Ready]')
    partial = sum(1 for v in versions if get_version_status(v) == '[Partial]')

    if complete:
        print(f"  {Colors.GREEN}Complete: {complete}{Colors.ENDC}")
    if resume_ready:
        print(f"  {Colors.CYAN}Resume Ready: {resume_ready}{Colors.ENDC}")
    if partial:
        print(f"  {Colors.YELLOW}Partial: {partial}{Colors.ENDC}")

    # Library info
    library_dir = Path.cwd() / 'cv_library'
    if library_dir.exists():
        library_files = list(library_dir.glob('*.json'))
        if library_files:
            print(f"\n{Colors.BOLD}CV Library:{Colors.ENDC}")
            for lib_file in library_files:
                with open(lib_file, 'r') as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else len(data.keys())
                    print(f"  - {lib_file.name}: {count} entries")


def interactive_menu() -> None:
    """Show interactive menu and handle user selection."""
    while True:
        clear_screen()

        # Header with box drawing
        width = 70
        print(f"{Colors.CYAN}╔{'═' * (width - 2)}╗{Colors.ENDC}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{'Resume Pipeline Manager'.center(width - 2)}{Colors.ENDC}{Colors.CYAN}║{Colors.ENDC}")  # noqa e501
        print(f"{Colors.CYAN}╚{'═' * (width - 2)}╝{Colors.ENDC}\n")

        # Current version with better formatting
        current_version = get_current_version()
        status = get_version_status(current_version)
        versions = get_available_versions()

        # Status color based on completeness
        if status == '[Complete]':
            status_colored = f"{Colors.GREEN}{status}{Colors.ENDC}"
        elif status == '[Resume Ready]':
            status_colored = f"{Colors.CYAN}{status}{Colors.ENDC}"
        else:
            status_colored = f"{Colors.YELLOW}{status}{Colors.ENDC}"

        print(f"  {Colors.DIM}Current:{Colors.ENDC} {Colors.BOLD}{current_version}{Colors.ENDC} {status_colored}")
        print(f"  {Colors.DIM}Total versions:{Colors.ENDC} {len(versions)}\n")

        print(f"{Colors.CYAN}┌─ Version Management{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC}  {Colors.BOLD}1{Colors.ENDC} › Create new version")
        print(f"{Colors.CYAN}│{Colors.ENDC}  {Colors.BOLD}2{Colors.ENDC} › Switch version")
        print(f"{Colors.CYAN}│{Colors.ENDC}  {Colors.BOLD}3{Colors.ENDC} › Duplicate version")
        print(f"{Colors.CYAN}│{Colors.ENDC}  {Colors.BOLD}4{Colors.ENDC} › Delete version")
        print(f"{Colors.CYAN}│{Colors.ENDC}  {Colors.BOLD}5{Colors.ENDC} › List all versions")

        print(f"\n{Colors.GREEN}┌─ Build & Validate{Colors.ENDC}")
        print(f"{Colors.GREEN}│{Colors.ENDC}  {Colors.BOLD}6{Colors.ENDC} › Build resume/cover letter")
        print(f"{Colors.GREEN}│{Colors.ENDC}  {Colors.BOLD}7{Colors.ENDC} › Validate current version")
        print(f"{Colors.GREEN}│{Colors.ENDC}  {Colors.BOLD}8{Colors.ENDC} › Export to markdown")
        print(f"{Colors.GREEN}│{Colors.ENDC}  {Colors.BOLD}9{Colors.ENDC} › Clean build artifacts")

        print(f"\n{Colors.YELLOW}┌─ Tools{Colors.ENDC}")
        print(f"{Colors.YELLOW}│{Colors.ENDC} {Colors.BOLD}10{Colors.ENDC} › Refresh CV library (JSON)")
        print(f"{Colors.YELLOW}│{Colors.ENDC} {Colors.BOLD}11{Colors.ENDC} › Refresh VS Code tasks")
        print(f"{Colors.YELLOW}│{Colors.ENDC} {Colors.BOLD}12{Colors.ENDC} › Show status")

        print(f"\n  {Colors.DIM}{Colors.BOLD}0{Colors.ENDC}{Colors.DIM} › Exit{Colors.ENDC}")

        choice = input(f"\n{Colors.BOLD}›{Colors.ENDC} ").strip().lower()

        if choice == '0' or choice == '' or choice == 'q' or choice == 'quit' or choice == 'exit':
            clear_screen()
            print(f"\n  {Colors.CYAN}Thanks for using Resume Pipeline!{Colors.ENDC}\n")
            break
        elif choice == '1':
            create_new_version()
        elif choice == '2':
            select_version_interactive()
        elif choice == '3':
            # Interactive duplicate - select source
            versions = get_available_versions()
            if not versions:
                print_error("No versions available to duplicate")
                continue

            print(f"\n{Colors.BOLD}Available versions:{Colors.ENDC}")
            for i, v in enumerate(versions, 1):
                print(f"  {i}. {v}")

            try:
                src_choice = input(f"\n{Colors.BOLD}Select source version (1-{len(versions)}): {Colors.ENDC}").strip()
                src_idx = int(src_choice) - 1
                if 0 <= src_idx < len(versions):
                    duplicate_version(versions[src_idx])
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Invalid input")

        elif choice == '4':
            # Interactive delete - select version
            versions = get_available_versions()
            if not versions:
                print_error("No versions available to delete")
                continue

            print(f"\n{Colors.BOLD}Available versions:{Colors.ENDC}")
            for i, v in enumerate(versions, 1):
                current_marker = " ← current" if v == current_version else ""
                print(f"  {i}. {v}{current_marker}")

            try:
                del_choice = input(f"\n{Colors.BOLD}Select version to delete (1-{len(versions)}): {Colors.ENDC}").strip()  # noqa e501
                if not del_choice:
                    print_info("Cancelled")
                    continue
                del_idx = int(del_choice) - 1
                if 0 <= del_idx < len(versions):
                    delete_version(versions[del_idx])
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Invalid input")

        elif choice == '5':
            list_versions()
        elif choice == '6':
            build_resume()
        elif choice == '7':
            validate_version()
        elif choice == '8':
            export_to_markdown()
        elif choice == '9':
            clean_build_artifacts()
        elif choice == '10':
            refresh_library()
        elif choice == '11':
            refresh_vscode_tasks()
        elif choice == '12':
            show_status()
        else:
            print_error("Invalid option")

        # Pause before showing menu again
        print()
        input(f"  {Colors.DIM}Press Enter to return to menu...{Colors.ENDC}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Resume Pipeline Manager - Manage your resume versions and builds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py                             # Interactive mode
  python pipeline.py --new-version acme_corp     # Create new version
  python pipeline.py --set-version               # Select version interactively
  python pipeline.py --list                      # List all versions
  python pipeline.py --build                     # Build current version
  python pipeline.py --validate                  # Validate current version
  python pipeline.py --export                    # Export current version to markdown
  python pipeline.py --duplicate acme_corp tech  # Duplicate acme_corp to tech
  python pipeline.py --delete old_version        # Delete a version
  python pipeline.py --clean                     # Clean build artifacts
  python pipeline.py --clean-all                 # Deep clean (includes PDFs and outputs)
  python pipeline.py --refresh-library           # Regenerate CV library
  python pipeline.py --status                    # Show pipeline status

For more information, see scripts/README.md
        """
    )

    parser.add_argument(
        '--new-version',
        metavar='NAME',
        nargs='?',
        const='',
        help='Create a new resume version (interactive if no name provided)'
    )

    parser.add_argument(
        '--set-version',
        metavar='NAME',
        nargs='?',
        const='',
        help='Set current version (interactive if no name provided)'
    )

    parser.add_argument(
        '--build',
        action='store_true',
        help='Build resume for current version'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available versions'
    )

    parser.add_argument(
        '--refresh-library',
        action='store_true',
        help='Regenerate CV library JSON files'
    )

    parser.add_argument(
        '--refresh-tasks',
        action='store_true',
        help='Regenerate VS Code tasks.json'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show pipeline status'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean LaTeX build artifacts and temporary files'
    )

    parser.add_argument(
        '--clean-all',
        action='store_true',
        help='Deep clean: remove all build artifacts, PDFs, and output directories'
    )

    parser.add_argument(
        '--validate',
        metavar='VERSION',
        nargs='?',
        const='',
        help='Validate version for errors (current version if not specified)'
    )

    parser.add_argument(
        '--export',
        metavar='VERSION',
        nargs='?',
        const='',
        help='Export version to markdown (current version if not specified)'
    )

    parser.add_argument(
        '--duplicate',
        metavar=('SOURCE', 'DEST'),
        nargs='+',
        help='Duplicate a version (SOURCE [DEST]). If DEST not provided, prompts interactively.'
    )

    parser.add_argument(
        '--delete',
        metavar='VERSION',
        help='Delete a version (requires confirmation)'
    )

    args = parser.parse_args()

    # Handle command-line arguments
    if args.new_version is not None:
        version_name = args.new_version if args.new_version else None
        create_new_version(version_name)

    elif args.set_version is not None:
        if args.set_version:
            # Set specific version
            update_version(args.set_version)
            print_success(f"Switched to version: {args.set_version}")
        else:
            # Interactive selection
            select_version_interactive()

    elif args.build:
        build_resume()

    elif args.list:
        list_versions()

    elif args.refresh_library:
        refresh_library()

    elif args.refresh_tasks:
        refresh_vscode_tasks()

    elif args.status:
        show_status()

    elif args.clean or args.clean_all:
        clean_build_artifacts(clean_all=args.clean_all)

    elif args.validate is not None:
        version = args.validate if args.validate else None
        validate_version(version)

    elif args.export is not None:
        version = args.export if args.export else None
        export_to_markdown(version)

    elif args.duplicate:
        # Parse source and optional destination
        if len(args.duplicate) == 1:
            # Only source provided, dest will be prompted
            duplicate_version(args.duplicate[0], None)
        elif len(args.duplicate) == 2:
            # Both source and dest provided
            duplicate_version(args.duplicate[0], args.duplicate[1])
        else:
            print_error("Invalid arguments for --duplicate. Use: --duplicate SOURCE [DEST]")

    elif args.delete:
        delete_version(args.delete)

    else:
        # No arguments provided - show interactive menu
        interactive_menu()


if __name__ == '__main__':
    main()
