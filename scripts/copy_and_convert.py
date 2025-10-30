#!/usr/bin/env python3
"""
PDF Copy and Markdown Converter
Post-build script for LaTeX compilation that:
1. Copies the generated PDF to the output directory with proper naming
2. Generates markdown version of the document

Usage:
    python copy_and_convert.py resume <jobname> <version>
    python copy_and_convert.py coverletter <jobname> <version>
"""

import sys
import time
import shutil
from pathlib import Path
from typing import Literal

# Add scripts directory to path for cv_utils import
sys.path.insert(0, str(Path(__file__).parent))
from cv_utils import (  # noqa: E402
    ProjectPaths,
    extract_name_from_personal_details,
    ensure_dir_exists,
    print_status,
    handle_error,
)


def copy_pdf(
    doc_type: Literal['resume', 'coverletter'],
    jobname: str,
    version: str,
    paths: ProjectPaths
) -> bool:
    """
    Copy PDF to output directory with proper naming.

    Args:
        doc_type: Type of document ('resume' or 'coverletter')
        jobname: LaTeX job name (source PDF filename without .pdf)
        version: Output version name
        paths: ProjectPaths instance

    Returns:
        True if successful, False otherwise
    """
    # Get full name from personal details
    full_name = extract_name_from_personal_details(paths.personal_details_file)

    # Determine document type name
    doc_type_name = "Resume" if doc_type == 'resume' else "Cover Letter"

    # Source PDF (LaTeX output)
    source_pdf = paths.base_dir / f"{jobname}.pdf"

    # Destination directory and filename
    output_dir = paths.output_version_dir(version)
    ensure_dir_exists(output_dir)

    dest_filename = f"{full_name} {doc_type_name}.pdf"
    dest_pdf = output_dir / dest_filename

    # Wait for PDF to be fully written (with retry logic)
    max_retries = 10
    retry_delay = 0.2  # 200ms between retries

    for attempt in range(max_retries):
        if source_pdf.exists():
            # Extra delay to ensure file is completely written and closed
            time.sleep(0.1)
            try:
                # Try to open the file to verify it's not locked
                with open(source_pdf, 'rb') as f:
                    f.read(1)
                break  # File is accessible, proceed
            except (IOError, PermissionError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print_status(f"PDF may still be locked after {max_retries} attempts", 'warning')
        else:
            time.sleep(retry_delay)

    if not source_pdf.exists():
        print_status(f"Source PDF not found: {source_pdf}", 'error')
        # Log to file for debugging LaTeX hooks
        with open(paths.base_dir / 'copy_debug.log', 'a') as f:
            f.write(f"Error: Source PDF not found: {source_pdf}\n")
        return False

    # Copy the file
    try:
        shutil.copy2(source_pdf, dest_pdf)
        print_status(f"Copied: {dest_pdf}", 'success')

        # Clean up source PDF from main directory
        try:
            source_pdf.unlink()
            print_status(f"Cleaned up: {source_pdf}", 'success')
        except Exception as cleanup_error:
            print_status(f"Could not remove source PDF: {cleanup_error}", 'warning')

        return True
    except FileNotFoundError:
        print_status(f"Source PDF not found: {source_pdf}", 'error')
        return False
    except Exception as e:
        print_status(f"Error copying PDF: {e}", 'error')
        return False


def run_markdown_conversion(doc_type: Literal['resume', 'coverletter'], paths: ProjectPaths) -> None:
    """
    Run the appropriate markdown conversion script.

    Args:
        doc_type: Type of document ('resume' or 'coverletter')
        paths: ProjectPaths instance
    """
    if doc_type == 'resume':
        script = paths.scripts_dir / "resume_to_markdown.py"
    else:
        script = paths.scripts_dir / "cover_letter_to_markdown.py"

    if not script.exists():
        print_status(f"Markdown conversion script not found: {script}", 'warning')
        return

    try:
        # Import and run the conversion script
        import importlib.util
        spec = importlib.util.spec_from_file_location("converter", script)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # The script runs on import via if __name__ == '__main__'
            # So we need to call main() directly if it exists
            if hasattr(module, 'main'):
                module.main()
    except Exception as e:
        print_status(f"Markdown conversion failed: {e}", 'warning')
        # Don't exit - markdown is optional


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: python copy_and_convert.py <resume|coverletter> <jobname> <version>")
        print("Example: python copy_and_convert.py resume cv-resume generic")
        sys.exit(1)

    doc_type = sys.argv[1].lower()
    jobname = sys.argv[2]
    version = sys.argv[3]

    # Validate document type
    if doc_type not in ('resume', 'coverletter'):
        handle_error(f"Document type must be 'resume' or 'coverletter', got: {doc_type}")

    # Initialize project paths
    paths = ProjectPaths()

    # Copy PDF with proper naming
    success = copy_pdf(doc_type, jobname, version, paths)

    if not success:
        handle_error(f"Failed to copy PDF for {doc_type}")

    # Generate markdown version
    run_markdown_conversion(doc_type, paths)

    print_status(f"Post-build complete for {doc_type}", 'success')


if __name__ == '__main__':
    main()
