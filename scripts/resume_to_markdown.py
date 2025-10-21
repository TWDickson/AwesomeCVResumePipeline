#!/usr/bin/env python3
"""
LaTeX Resume to Markdown Converter
Converts Your Name's LaTeX resume to clean Markdown format.
"""

import re
import sys
from pathlib import Path
from typing import Dict


def clean_latex_text(text: str) -> str:
    """Remove LaTeX commands and clean up text."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

    # Remove common LaTeX commands but keep their content
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)

    # Remove various LaTeX spacing commands
    text = re.sub(r'\\enskip|\\quad|\\qquad|~', ' ', text)
    text = re.sub(r'\\cdotp', '·', text)

    # Clean up special characters
    text = re.sub(r'\\&', '&', text)
    text = re.sub(r'\\_', '_', text)
    text = re.sub(r'\\%', '%', text)
    text = re.sub(r'\\\$', '$', text)

    # Remove remaining backslash commands
    text = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?', '', text)

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


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


def extract_tagline(tagline_path: Path) -> str:
    """Extract position/tagline from tagline.tex."""
    with open(tagline_path, 'r', encoding='utf-8') as f:
        content = f.read()

    position_match = re.search(r'\\position\{([^}]+)\}', content)
    if position_match:
        tagline = clean_latex_text(position_match.group(1))
        # Skip placeholders
        if '[Your Title]' not in tagline and tagline.strip():
            return tagline
    return ""


def extract_summary(summary_path: Path) -> str:
    """Extract summary section from summary.tex."""
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract content between \begin{cvparagraph} and \end{cvparagraph}
    summary_match = re.search(r'\\begin\{cvparagraph\}(.*?)\\end\{cvparagraph\}', content, re.DOTALL)
    if summary_match:
        return clean_latex_text(summary_match.group(1))
    return ""


def extract_skills(skills_path: Path) -> str:
    """Extract skills from skills.tex."""
    with open(skills_path, 'r', encoding='utf-8') as f:
        content = f.read()

    skills = []

    # Find all \cvskill entries
    skill_pattern = r'\\cvskill\s*\{([^}]+)\}\s*%[^\n]*\n\s*\{([^}]+)\}'
    matches = re.finditer(skill_pattern, content, re.MULTILINE)

    for match in matches:
        category = clean_latex_text(match.group(1))
        skills_list = clean_latex_text(match.group(2))
        skills.append({'category': category, 'skills': skills_list})

    return skills


def extract_experience(experience_path: Path) -> str:
    """Extract experience section from experience.tex."""
    with open(experience_path, 'r', encoding='utf-8') as f:
        content = f.read()

    experiences = []

    # Split content by \cventry
    entries = re.split(r'\\cventry', content)[1:]  # Skip first empty split

    for entry in entries:
        # Extract the five main groups
        # Pattern: {title} {org} {location} {date} {items_block}
        parts_match = re.match(
            r'\s*\{([^}]+)\}\s*%[^\n]*\n'  # title
            r'\s*\{([^}]+)\}\s*%[^\n]*\n'  # organization
            r'\s*\{([^}]+)\}\s*%[^\n]*\n'  # location
            r'\s*\{([^}]+)\}\s*%[^\n]*\n'  # dates
            r'\s*\{(.*)\}',  # items block (greedy to capture all)
            entry, re.DOTALL
        )

        if not parts_match:
            continue

        title = clean_latex_text(parts_match.group(1))
        organization = clean_latex_text(parts_match.group(2))
        location = clean_latex_text(parts_match.group(3))
        dates = clean_latex_text(parts_match.group(4))
        items_block = parts_match.group(5)

        # Extract bullet points - look for \item commands
        items = []
        # Split by \item and process each
        item_parts = re.split(r'\\item\s*', items_block)[1:]  # Skip first empty split

        for item_part in item_parts:
            # Extract content within braces (handling nested braces)
            if item_part.strip().startswith('{'):
                # Find matching closing brace
                brace_count = 0
                end_pos = 0
                for i, char in enumerate(item_part):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i
                            break

                if end_pos > 0:
                    item_text = clean_latex_text(item_part[1:end_pos])
                    if item_text:
                        items.append(item_text)

        experiences.append({
            'title': title,
            'organization': organization,
            'location': location,
            'dates': dates,
            'items': items
        })

    return experiences


def generate_markdown(base_path: Path, version: str) -> str:
    """Generate markdown resume from LaTeX files."""
    base_path = Path(base_path)

    # Extract all components
    personal_info = extract_personal_info(base_path / 'cv-personal-details.tex')

    cv_path = base_path / '_content' / version
    tagline = extract_tagline(cv_path / 'tagline.tex')
    summary = extract_summary(cv_path / 'summary.tex')
    skills = extract_skills(cv_path / 'skills.tex')
    experiences = extract_experience(cv_path / 'experience.tex')

    # Build markdown
    md_lines = []

    # Header
    md_lines.append(f"# {personal_info.get('name', '')}")
    if tagline:
        md_lines.append(f"\n*{tagline}*\n")

    # Contact info
    contact_parts = []
    if 'email' in personal_info:
        contact_parts.append(f"📧 {personal_info['email']}")
    if 'mobile' in personal_info:
        contact_parts.append(f"📱 {personal_info['mobile']}")
    if 'homepage' in personal_info:
        contact_parts.append(f"🌐 {personal_info['homepage']}")
    if 'github' in personal_info:
        contact_parts.append(f"💻 github.com/{personal_info['github']}")
    if 'linkedin' in personal_info:
        contact_parts.append(f"💼 linkedin.com/in/{personal_info['linkedin']}")

    md_lines.append(" | ".join(contact_parts))
    md_lines.append("")

    # Summary
    if summary:
        md_lines.append("## Summary\n")
        md_lines.append(summary)
        md_lines.append("")

    # Skills
    if skills:
        md_lines.append("## Skills\n")
        for skill in skills:
            md_lines.append(f"**{skill['category']}:** {skill['skills']}\n")
        md_lines.append("")

    # Experience
    if experiences:
        md_lines.append("## Experience\n")
        for exp in experiences:
            md_lines.append(f"### {exp['title']}")
            md_lines.append(f"**{exp['organization']}** | {exp['location']} | {exp['dates']}\n")
            for item in exp['items']:
                md_lines.append(f"- {item}")
            md_lines.append("")

    return "\n".join(md_lines)


def main() -> None:
    """Main function to convert resume."""
    # Get base path (pipeline directory) and version
    base_path = Path(__file__).resolve().parent.parent

    # Read version from main tex file
    main_tex = base_path / 'cv-resume.tex'
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
        print("Error: Could not find OutputVersion in cv-resume.tex or cv-version.tex")
        sys.exit(1)

    version = version_match.group(1)
    print(f"Converting version: {version}")

    # Generate markdown
    markdown = generate_markdown(base_path, version)

    # Create output directory if it doesn't exist
    output_dir = base_path / '_output' / version
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write to file
    output_path = output_dir / f"Your Name Resume - {version}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Markdown resume generated: {output_path}")


if __name__ == '__main__':
    main()
