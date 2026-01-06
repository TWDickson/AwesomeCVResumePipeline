#!/usr/bin/env python3
"""
LaTeX Resume to Markdown Converter
Converts Your Name's LaTeX resume to clean Markdown format.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add scripts directory to path for cv_utils import
sys.path.insert(0, str(Path(__file__).parent))

from cv_utils import (  # noqa: E402
    clean_latex_text,
    read_text_file,
    write_text_file,
    read_text_file_safe,
    ensure_dir_exists,
    extract_personal_info,
    get_current_version,
    ProjectPaths,
)


def extract_tagline(tagline_path: Path) -> str:
    """Extract position/tagline from tagline.tex."""
    content = read_text_file(tagline_path)

    # Use greedy match to handle nested braces (common in taglines with separators)
    position_match = re.search(r'\\position\{(.+)\}', content, re.DOTALL)
    if position_match:
        tagline = clean_latex_text(position_match.group(1))
        # Skip placeholders
        if '[Your Title]' not in tagline and tagline.strip():
            return tagline
    return ""


def extract_summary(summary_path: Path) -> str:
    """Extract summary section from summary.tex."""
    content = read_text_file(summary_path)

    # Extract content between \begin{cvparagraph} and \end{cvparagraph}
    summary_match = re.search(r'\\begin\{cvparagraph\}(.*?)\\end\{cvparagraph\}', content, re.DOTALL)
    if summary_match:
        return clean_latex_text(summary_match.group(1))
    return ""


def extract_skills(skills_path: Path) -> List[Dict[str, str]]:
    """Extract skills from skills.tex."""
    content = read_text_file_safe(skills_path)
    if not content:
        return []

    skills = []

    # Find all \cvskill entries - handle both with and without comments
    # Pattern: \cvskill{category}{skills}
    # Also handles multiline format with comments between braces
    skill_pattern = r'\\cvskill\s*\{([^}]+)\}\s*(?:%[^\n]*)?\s*\{([^}]+)\}'
    matches = re.finditer(skill_pattern, content, re.MULTILINE)

    for match in matches:
        category = clean_latex_text(match.group(1))
        skills_list = clean_latex_text(match.group(2))
        skills.append({'category': category, 'skills': skills_list})

    return skills


def extract_experience(experience_path: Path) -> List[Dict[str, Any]]:
    """Extract experience section from experience.tex."""
    content = read_text_file_safe(experience_path)
    if not content:
        return []

    experiences = []

    # Robust parsing: find all \cventry occurrences and extract five brace-delimited args
    cventry_pattern = r'\\cventry\s*%?\s*'
    for match in re.finditer(cventry_pattern, content):
        pos = match.end()

        # Extract 5 brace-delimited arguments
        args = []
        for _ in range(5):
            # Skip whitespace and line comments
            while pos < len(content) and content[pos] in ' \t\n':
                pos += 1

            # Skip a line comment starting with % until end of line
            if pos < len(content) and content[pos] == '%':
                # advance to end of line
                while pos < len(content) and content[pos] != '\n':
                    pos += 1
                continue

            if pos >= len(content) or content[pos] != '{':
                break

            # Extract balanced braces content
            brace_count = 0
            i = pos
            extracted = ''
            for i in range(pos, len(content)):
                ch = content[i]
                if ch == '{':
                    brace_count += 1
                    if brace_count > 1:
                        extracted += ch
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                    else:
                        extracted += ch
                else:
                    if brace_count >= 1:
                        extracted += ch

            args.append(extracted.strip())
            pos = i + 1

        if len(args) < 5:
            continue

        title, organization, location, dates, items_block = args[:5]

        title = clean_latex_text(title)
        organization = clean_latex_text(organization)
        location = clean_latex_text(location)
        dates = clean_latex_text(dates)

        # Extract bullet points
        items = []
        item_parts = re.split(r'\\item\s+', items_block)
        for part in item_parts[1:]:
            item_text = re.split(r'\\end\{cvitems\}', part)[0].strip()
            if item_text:
                item_text = clean_latex_text(item_text)
                if item_text:
                    # Remove stray surrounding braces left from parsing
                    if item_text.startswith('{') and item_text.endswith('}'):
                        item_text = item_text[1:-1].strip()
                    items.append(item_text)

        experiences.append({
            'title': title,
            'organization': organization,
            'location': location,
            'dates': dates,
            'items': items
        })
    return experiences


def extract_cvhonors(file_path: Path) -> List[Dict[str, str]]:
    """Extract honors/certificates/committees from cvhonors environment.

    These use \\cvhonor{name}{organization}{location}{date}
    """
    content = read_text_file_safe(file_path)
    if not content:
        return []

    honors = []

    # Check for subsections (used in honors.tex)
    subsection_pattern = r'\\cvsubsection\{([^}]+)\}'
    subsection_matches = list(re.finditer(subsection_pattern, content))

    # Split content by subsections if they exist
    if subsection_matches:
        # Process each subsection
        for i, subsection_match in enumerate(subsection_matches):
            subsection_name = clean_latex_text(subsection_match.group(1))

            # Get content from this subsection to the next one (or end)
            start_pos = subsection_match.end()
            end_pos = subsection_matches[i + 1].start() if i + 1 < len(subsection_matches) else len(content)
            section_content = content[start_pos:end_pos]

            # Find cvhonor entries in this subsection
            honor_pattern = r'\\cvhonor\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}'
            for match in re.finditer(honor_pattern, section_content):
                name = clean_latex_text(match.group(1))
                organization = clean_latex_text(match.group(2))
                location = clean_latex_text(match.group(3))
                date = clean_latex_text(match.group(4))

                # Skip template placeholders
                if '[' in name or not name:
                    continue

                honors.append({
                    'subsection': subsection_name,
                    'name': name,
                    'organization': organization,
                    'location': location,
                    'date': date
                })
    else:
        # No subsections, just find all cvhonor entries
        honor_pattern = r'\\cvhonor\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}'
        for match in re.finditer(honor_pattern, content):
            name = clean_latex_text(match.group(1))
            organization = clean_latex_text(match.group(2))
            location = clean_latex_text(match.group(3))
            date = clean_latex_text(match.group(4))

            # Skip template placeholders
            if '[' in name or not name:
                continue

            honors.append({
                'name': name,
                'organization': organization,
                'location': location,
                'date': date
            })

    return honors


def extract_cventries_generic(file_path: Path) -> List[Dict[str, Any]]:
    """Extract entries from cventries environment (education, writing, presentations, extracurricular).

    These use \\cventry{title}{org}{location}{date}{items}
    Same structure as experience.
    """
    content = read_text_file_safe(file_path)
    if not content:
        return []

    entries = []

    # Robust parsing similar to extract_experience
    cventry_pattern = r'\\cventry\s*%?\s*'
    for match in re.finditer(cventry_pattern, content):
        pos = match.end()

        args = []
        for _ in range(5):
            while pos < len(content) and content[pos] in ' \t\n':
                pos += 1
            if pos < len(content) and content[pos] == '%':
                while pos < len(content) and content[pos] != '\n':
                    pos += 1
                continue
            if pos >= len(content) or content[pos] != '{':
                break

            brace_count = 0
            extracted = ''
            for i in range(pos, len(content)):
                ch = content[i]
                if ch == '{':
                    brace_count += 1
                    if brace_count > 1:
                        extracted += ch
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                    else:
                        extracted += ch
                else:
                    if brace_count >= 1:
                        extracted += ch

            args.append(extracted.strip())
            pos = i + 1

        if len(args) < 5:
            continue

        title, organization, location, dates, items_block = args[:5]

        title = clean_latex_text(title)
        organization = clean_latex_text(organization)
        location = clean_latex_text(location)
        dates = clean_latex_text(dates)

        if '[' in title or not title:
            continue

        items = []
        item_parts = re.split(r'\\item\s+', items_block)
        for part in item_parts[1:]:
            item_text = re.split(r'\\end\{cvitems\}', part)[0].strip()
            if item_text:
                item_text = clean_latex_text(item_text)
                if item_text and '[' not in item_text:
                    if item_text.startswith('{') and item_text.endswith('}'):
                        item_text = item_text[1:-1].strip()
                    items.append(item_text)

        entries.append({
            'title': title,
            'organization': organization,
            'location': location,
            'dates': dates,
            'items': items
        })

    return entries


def extract_section_order(cv_resume_path: Path) -> List[str]:
    """Extract the section order from cv-resume.tex \\loadSections command."""
    content = read_text_file(cv_resume_path)

    # Find \loadSections{section1, section2, section3}
    section_match = re.search(r'\\loadSections\{([^}]+)\}', content)
    if section_match:
        sections_str = section_match.group(1)
        # Split by commas and strip whitespace
        sections = [s.strip() for s in sections_str.split(',')]
        return sections

    # Default fallback
    return ['summary', 'skills', 'experience']


def generate_markdown(base_path: Path, version: str) -> str:
    """Generate markdown resume from LaTeX files."""
    base_path = Path(base_path)
    cv_path = base_path / '_content' / version

    # Extract personal info and tagline
    personal_info = extract_personal_info(base_path / 'cv-personal-details.tex')
    tagline = extract_tagline(cv_path / 'tagline.tex')

    # Get section order from cv-resume.tex
    section_order = extract_section_order(base_path / 'cv-resume.tex')

    # Load all sections into a dictionary
    sections_data = {}

    for section_name in section_order:
        section_file = cv_path / f'{section_name}.tex'

        if section_name == 'summary':
            sections_data['summary'] = extract_summary(section_file)
        elif section_name == 'skills':
            sections_data['skills'] = extract_skills(section_file)
        elif section_name == 'experience':
            sections_data['experience'] = extract_experience(section_file)
        elif section_name in ['education', 'writing', 'presentation', 'extracurricular']:
            sections_data[section_name] = extract_cventries_generic(section_file)
        elif section_name in ['certificates', 'honors', 'committees']:
            sections_data[section_name] = extract_cvhonors(section_file)

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

    # Generate sections dynamically based on order
    for section_name in section_order:
        section_data = sections_data.get(section_name)

        if not section_data:
            continue

        # Section title mapping
        section_titles = {
            'summary': 'Summary',
            'skills': 'Skills',
            'experience': 'Experience',
            'education': 'Education',
            'certificates': 'Certificates',
            'honors': 'Honors & Awards',
            'committees': 'Program Committees',
            'writing': 'Writing',
            'presentation': 'Presentations',
            'extracurricular': 'Extracurricular Activity'
        }

        section_title = section_titles.get(section_name, section_name.title())

        if section_name == 'summary':
            md_lines.append(f"## {section_title}\n")
            md_lines.append(section_data)
            md_lines.append("")

        elif section_name == 'skills':
            md_lines.append(f"## {section_title}\n")
            for skill in section_data:
                md_lines.append(f"**{skill['category']}:** {skill['skills']}\n")
            md_lines.append("")

        elif section_name in ['experience', 'education', 'writing', 'presentation', 'extracurricular']:
            md_lines.append(f"## {section_title}\n")
            for entry in section_data:
                md_lines.append(f"### {entry['title']}")
                md_lines.append(f"**{entry['organization']}** | {entry['location']} | {entry['dates']}\n")
                for item in entry['items']:
                    md_lines.append(f"- {item}")
                md_lines.append("")

        elif section_name in ['certificates', 'honors', 'committees']:
            md_lines.append(f"## {section_title}\n")

            # Check if we have subsections (like in honors)
            has_subsections = any('subsection' in item for item in section_data)

            if has_subsections:
                # Group by subsection
                current_subsection = None
                for item in section_data:
                    if item.get('subsection') != current_subsection:
                        current_subsection = item['subsection']
                        md_lines.append(f"### {current_subsection}\n")

                    # Format the honor entry
                    parts = [item['name'], item['organization']]
                    if item.get('location'):
                        parts.append(item['location'])
                    parts.append(item['date'])
                    md_lines.append("- " + " | ".join(parts))
                md_lines.append("")
            else:
                # No subsections, just list items
                for item in section_data:
                    parts = [item['name'], item['organization']]
                    if item.get('location'):
                        parts.append(item['location'])
                    parts.append(item['date'])
                    md_lines.append("- " + " | ".join(parts))
                md_lines.append("")

    return "\n".join(md_lines)


def main() -> None:
    """Main function to convert resume."""
    # Initialize project paths
    paths = ProjectPaths()

    # Get current version
    version = get_current_version(paths.version_file)

    if not version:
        print("Error: Could not find OutputVersion in cv-version.tex")
        sys.exit(1)

    print(f"Converting version: {version}")

    # Generate markdown
    markdown = generate_markdown(paths.base_dir, version)

    # Create output directory if it doesn't exist
    output_dir = paths.output_version_dir(version)
    ensure_dir_exists(output_dir)

    # Write to file
    output_path = output_dir / f"Taylor Dickson Resume - {version}.md"
    write_text_file(output_path, markdown)

    print(f"✓ Markdown resume generated: {output_path}")


if __name__ == '__main__':
    main()
