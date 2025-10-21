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


def extract_name_from_personal_details(personal_details_path: Path) -> str:
    """
    Extract the full name from cv-personal-details.tex.

    Returns:
        Full name in format "FirstName LastName"
    """
    try:
        content = personal_details_path.read_text(encoding='utf-8')

        # Look for \name{First}{Last}
        import re
        name_match = re.search(r'\\name\{([^}]+)\}\{([^}]+)\}', content)

        if name_match:
            first_name = name_match.group(1).strip()
            last_name = name_match.group(2).strip()
            return f"{first_name} {last_name}"

        # Fallback
        return "CV"
    except Exception as e:
        print(f"Warning: Could not extract name from personal details: {e}")
        return "CV"


def copy_pdf(
    doc_type: Literal['resume', 'coverletter'],
    jobname: str,
    version: str,
    base_dir: Path
) -> Path:
    """
    Copy PDF to output directory with proper naming.

    Args:
        doc_type: Type of document ('resume' or 'coverletter')
        jobname: LaTeX job name (source PDF filename without .pdf)
        version: Output version name
        base_dir: Base directory (pipeline root)

    Returns:
        Path to the copied PDF file
    """
    # Get full name from personal details
    personal_details = base_dir / "cv-personal-details.tex"
    full_name = extract_name_from_personal_details(personal_details)

    # Determine document type name
    doc_type_name = "Resume" if doc_type == 'resume' else "Cover Letter"

    # Source PDF (LaTeX output)
    source_pdf = base_dir / f"{jobname}.pdf"

    # Destination directory and filename
    output_dir = base_dir / "_output" / version
    output_dir.mkdir(parents=True, exist_ok=True)

    dest_filename = f"{full_name} {doc_type_name}.pdf"
    dest_pdf = output_dir / dest_filename

    # Small delay to ensure PDF is fully written
    time.sleep(0.1)

    # Copy the file
    try:
        shutil.copy2(source_pdf, dest_pdf)
        print(f"✓ Copied: {dest_pdf}")

        # Clean up source PDF from main directory
        try:
            source_pdf.unlink()
            print(f"✓ Cleaned up: {source_pdf}")
        except Exception as cleanup_error:
            print(f"Warning: Could not remove source PDF: {cleanup_error}")

        return dest_pdf
    except FileNotFoundError:
        print(f"Error: Source PDF not found: {source_pdf}")
        sys.exit(1)
    except Exception as e:
        print(f"Error copying PDF: {e}")
        sys.exit(1)


def run_markdown_conversion(doc_type: Literal['resume', 'coverletter'], base_dir: Path) -> None:
    """
    Run the appropriate markdown conversion script.

    Args:
        doc_type: Type of document ('resume' or 'coverletter')
        base_dir: Base directory (pipeline root)
    """
    script_dir = base_dir / "scripts"

    if doc_type == 'resume':
        script = script_dir / "resume_to_markdown.py"
    else:
        script = script_dir / "cover_letter_to_markdown.py"

    if not script.exists():
        print(f"Warning: Markdown conversion script not found: {script}")
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
        print(f"Warning: Markdown conversion failed: {e}")
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
        print(f"Error: Document type must be 'resume' or 'coverletter', got: {doc_type}")
        sys.exit(1)

    # Get base directory (pipeline root)
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent

    # Copy PDF with proper naming
    copy_pdf(doc_type, jobname, version, base_dir)

    # Generate markdown version
    run_markdown_conversion(doc_type, base_dir)

    print(f"✓ Post-build complete for {doc_type}")


if __name__ == '__main__':
    main()
