#!/usr/bin/env python3
"""
LaTeX Cover Letter to Markdown Converter
Converts Your Name's LaTeX cover letter to clean Markdown format.
"""

import re
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cv_utils.regex_parsing import clean_latex_text  # noqa: E402


def extract_personal_info(personal_details_path: Path) -> Dict[str, str]:
    """Extract personal information from cv-personal-details.tex."""
    with open(personal_details_path, 'r', encoding='utf-8') as f:
        content = f.read()

    info = {}

    # Extract name
    name_match = re.search(r'\\name\{([^}]+)\}\{([^}]+)\}', content)
    if name_match:
        info['name'] = f"{name_match.group(1)} {name_match.group(2)}"

    # Extract contact details
    mobile_match = re.search(r'\\mobile\{[^}]+\}\{([^}]+)\}', content)
    if mobile_match:
        info['mobile'] = mobile_match.group(1)

    email_match = re.search(r'\\email\{([^}]+)\}', content)
    if email_match:
        info['email'] = email_match.group(1)

    homepage_match = re.search(r'\\homepage\{([^}]+)\}', content)
    if homepage_match:
        info['homepage'] = homepage_match.group(1)

    github_match = re.search(r'\\github\{([^}]+)\}', content)
    if github_match:
        info['github'] = github_match.group(1)

    linkedin_match = re.search(r'\\linkedin\{([^}]+)\}', content)
    if linkedin_match:
        info['linkedin'] = linkedin_match.group(1)

    return info


def extract_cover_letter_info(cover_letter_path: Path) -> Dict[str, str]:
    """Extract cover letter content from cover_letter.tex."""
    with open(cover_letter_path, 'r', encoding='utf-8') as f:
        content = f.read()

    info = {}

    # Extract letter date
    date_match = re.search(r'\\storeletterdate\{([^}]+)\}', content)
    if date_match:
        info['date'] = clean_latex_text(date_match.group(1), handle_today=True)

    # Extract recipient
    recipient_match = re.search(r'\\storerecipient\{([^}]+)\}\{([^}]+)\}', content)
    if recipient_match:
        info['recipient_company'] = clean_latex_text(recipient_match.group(1))
        info['recipient_name'] = clean_latex_text(recipient_match.group(2))

    # Extract title
    title_match = re.search(r'\\storelettertitle\{([^}]+)\}', content)
    if title_match:
        info['title'] = clean_latex_text(title_match.group(1))

    # Extract opening
    opening_match = re.search(r'\\storeletteropening\{([^}]+)\}', content)
    if opening_match:
        info['opening'] = clean_latex_text(opening_match.group(1))

    # Extract closing
    closing_match = re.search(r'\\storeletterclosing\{([^}]+)\}', content)
    if closing_match:
        info['closing'] = clean_latex_text(closing_match.group(1))

    # Extract enclosure
    enclosure_match = re.search(r'\\storeletterenclosure(?:\[([^\]]+)\])?\{([^}]+)\}', content)
    if enclosure_match:
        info['enclosure_label'] = enclosure_match.group(1) if enclosure_match.group(1) else 'Enclosure'
        info['enclosure'] = clean_latex_text(enclosure_match.group(2))

    # Extract letter body - the content between \begin{storedcvletter}{ and }\end{storedcvletter}
    # Need to handle nested braces
    body_start = content.find(r'\begin{storedcvletter}{')
    if body_start != -1:
        # Find the position after the opening brace
        start_pos = body_start + len(r'\begin{storedcvletter}{')

        # Find matching closing brace before \end{storedcvletter}
        brace_count = 1
        end_pos = start_pos

        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break

        body_text = content[start_pos:end_pos]

        # Split into paragraphs (separated by blank lines)
        paragraphs = []
        current_para = []

        for line in body_text.split('\n'):
            # Skip comment-only lines
            if line.strip().startswith('%') and not line.strip().startswith('% '):
                continue
            # Remove inline comments but keep the text
            line = re.sub(r'%.*$', '', line)
            line = line.strip()

            if line:
                current_para.append(line)
            elif current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []

        if current_para:
            paragraphs.append(' '.join(current_para))

        # Clean each paragraph
        info['body_paragraphs'] = [clean_latex_text(p) for p in paragraphs if p.strip()]

    return info


def generate_markdown(base_path: Path, version: str) -> str:
    """Generate markdown cover letter from LaTeX files."""
    base_path = Path(base_path)

    # Extract all components
    personal_info = extract_personal_info(base_path / 'cv-personal-details.tex')

    cv_path = base_path / '_content' / version
    cover_letter_info = extract_cover_letter_info(cv_path / 'cover_letter.tex')

    # Build markdown
    md_lines = []

    # Header with name and contact
    md_lines.append(f"# {personal_info.get('name', '')}")

    # Contact info
    contact_parts = []
    if 'email' in personal_info:
        contact_parts.append(personal_info['email'])
    if 'mobile' in personal_info:
        contact_parts.append(personal_info['mobile'])
    if 'homepage' in personal_info:
        contact_parts.append(personal_info['homepage'])
    if 'linkedin' in personal_info:
        contact_parts.append(f"linkedin.com/in/{personal_info['linkedin']}")

    md_lines.append(" | ".join(contact_parts))
    md_lines.append("")

    # Date
    if 'date' in cover_letter_info:
        md_lines.append(cover_letter_info['date'])
        md_lines.append("")

    # Recipient
    if 'recipient_company' in cover_letter_info:
        md_lines.append(cover_letter_info['recipient_company'])
        if 'recipient_name' in cover_letter_info:
            md_lines.append(cover_letter_info['recipient_name'])
        md_lines.append("")

    # Title (if present and different from default)
    if 'title' in cover_letter_info and cover_letter_info['title']:
        md_lines.append(f"**Re: {cover_letter_info['title']}**")
        md_lines.append("")

    # Opening
    if 'opening' in cover_letter_info:
        md_lines.append(cover_letter_info['opening'])
        md_lines.append("")

    # Body paragraphs
    if 'body_paragraphs' in cover_letter_info:
        for para in cover_letter_info['body_paragraphs']:
            md_lines.append(para)
            md_lines.append("")

    # Closing
    if 'closing' in cover_letter_info:
        md_lines.append(cover_letter_info['closing'])
        md_lines.append("")
        md_lines.append(personal_info.get('name', ''))
        md_lines.append("")

    # Enclosure
    if 'enclosure' in cover_letter_info:
        label = cover_letter_info.get('enclosure_label', 'Enclosure')
        md_lines.append(f"*{label}: {cover_letter_info['enclosure']}*")

    return "\n".join(md_lines)


def main() -> None:
    """Main function to convert cover letter."""
    # Get base path (pipeline directory) and version
    base_path = Path(__file__).resolve().parent.parent

    # Read version from main tex file
    main_tex = base_path / 'cv-coverletter.tex'
    with open(main_tex, 'r', encoding='utf-8') as f:
        content = f.read()

    version_match = re.search(r'\\newcommand\{\\OutputVersion\}\{([^}]+)\}', content)

    # If not found in main file, check cv-version.tex
    if not version_match:
        cv_version_tex = base_path / 'cv-version.tex'
        if cv_version_tex.exists():
            with open(cv_version_tex, 'r', encoding='utf-8') as f:
                version_content = f.read()
            version_match = re.search(r'\\newcommand\{\\OutputVersion\}\{([^}]+)\}', version_content)

    if not version_match:
        print("Error: Could not find OutputVersion in cv-coverletter.tex or cv-version.tex")
        sys.exit(1)

    version = version_match.group(1)
    print(f"Converting cover letter version: {version}")

    # Generate markdown
    markdown = generate_markdown(base_path, version)

    # Create output directory if it doesn't exist
    output_dir = base_path / '_output' / version
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write to file
    output_path = output_dir / f"Your Name Cover Letter - {version}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Markdown cover letter generated: {output_path}")


if __name__ == '__main__':
    main()
