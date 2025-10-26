#!/usr/bin/env python3
"""
LaTeX Resume to Markdown Converter
Converts Your Name's LaTeX resume to clean Markdown format.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def clean_latex_text(text: str) -> str:
    """Remove LaTeX commands and clean up text."""
    # Handle escaped special characters using placeholders BEFORE removing comments
    # This prevents escaped % from being treated as comment markers
    text = re.sub(r'\\&', '__AMP__', text)
    text = re.sub(r'\\_', '__UNDERSCORE__', text)
    text = re.sub(r'\\%', '__PERCENT__', text)
    text = re.sub(r'\\\$', '__DOLLAR__', text)

    # Now remove comments (escaped % won't be matched)
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

    # Remove common LaTeX commands but keep their content
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)

    # Remove various LaTeX spacing commands and replace with space
    text = re.sub(r'\\enskip|\\quad|\\qquad|~', ' ', text)
    text = re.sub(r'\\cdotp', '·', text)

    # Remove nested braces that just contain spacing commands (common in taglines)
    # This handles cases like: Data Engineer{\enskip\cdotp\enskip}
    text = re.sub(r'\{(\s*·?\s*)\}', r'\1', text)

    # Remove remaining backslash commands
    text = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?', '', text)

    # Remove any leftover empty braces
    text = re.sub(r'\{\}', '', text)

    # Convert placeholders back to actual characters
    text = text.replace('__AMP__', '&')
    text = text.replace('__UNDERSCORE__', '_')
    text = text.replace('__PERCENT__', '%')
    text = text.replace('__DOLLAR__', '$')

    # Clean up whitespace (including multiple spaces and spaces around dots)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*·\s*', ' · ', text)  # Normalize spacing around separators
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
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract content between \begin{cvparagraph} and \end{cvparagraph}
    summary_match = re.search(r'\\begin\{cvparagraph\}(.*?)\\end\{cvparagraph\}', content, re.DOTALL)
    if summary_match:
        return clean_latex_text(summary_match.group(1))
    return ""


def extract_skills(skills_path: Path) -> List[Dict[str, str]]:
    """Extract skills from skills.tex."""
    if not skills_path.exists():
        return []

    with open(skills_path, 'r', encoding='utf-8') as f:
        content = f.read()

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
    if not experience_path.exists():
        return []

    with open(experience_path, 'r', encoding='utf-8') as f:
        content = f.read()

    experiences = []

    # Split content by \cventry
    entries = re.split(r'\\cventry%?\s*', content)[1:]  # Skip first empty split

    for entry in entries:
        # Extract the first four simple groups, then manually find the fifth with nested braces
        simple_match = re.match(
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # title
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # organization
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # location
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # dates
            r'\s*\{',  # Opening brace of items block
            entry, re.DOTALL
        )

        if not simple_match:
            continue

        title = clean_latex_text(simple_match.group(1))
        organization = clean_latex_text(simple_match.group(2))
        location = clean_latex_text(simple_match.group(3))
        dates = clean_latex_text(simple_match.group(4))

        # Find the items block by matching braces
        start_pos = simple_match.end()
        brace_count = 1
        end_pos = start_pos

        for i in range(start_pos, len(entry)):
            if entry[i] == '{':
                brace_count += 1
            elif entry[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break

        items_block = entry[start_pos:end_pos]

        # Extract bullet points - look for \item commands
        items = []
        # Split by \item and process each - \item doesn't use braces, text follows directly
        item_parts = re.split(r'\\item\s+', items_block)[1:]  # Skip first empty split

        for item_part in item_parts:
            # Each item goes until the next \item or end of block
            # Clean up and extract the text
            item_text = item_part.strip()
            # Remove trailing content after the item (like \end{cvitems})
            item_text = re.split(r'\\end\{cvitems\}', item_text)[0].strip()

            if item_text:
                item_text = clean_latex_text(item_text)
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


def extract_cvhonors(file_path: Path) -> List[Dict[str, str]]:
    """Extract honors/certificates/committees from cvhonors environment.

    These use \\cvhonor{name}{organization}{location}{date}
    """
    if not file_path.exists():
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

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
    if not file_path.exists():
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []

    # Split content by \cventry
    entry_parts = re.split(r'\\cventry%?\s*', content)[1:]  # Skip first empty split

    for entry in entry_parts:
        # Extract the first four simple groups, then manually find the fifth with nested braces
        simple_match = re.match(
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # title
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # organization
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # location
            r'\s*\{([^}]+)\}\s*%?[^\n]*\n?'  # dates
            r'\s*\{',  # Opening brace of items block
            entry, re.DOTALL
        )

        if not simple_match:
            continue

        title = clean_latex_text(simple_match.group(1))
        organization = clean_latex_text(simple_match.group(2))
        location = clean_latex_text(simple_match.group(3))
        dates = clean_latex_text(simple_match.group(4))

        # Skip template placeholders
        if '[' in title or not title:
            continue

        # Find the items block by matching braces
        start_pos = simple_match.end()
        brace_count = 1
        end_pos = start_pos

        for i in range(start_pos, len(entry)):
            if entry[i] == '{':
                brace_count += 1
            elif entry[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break

        items_block = entry[start_pos:end_pos]

        # Extract bullet points - look for \item commands
        items = []
        # Split by \item and process each - \item doesn't use braces, text follows directly
        item_parts = re.split(r'\\item\s+', items_block)[1:]  # Skip first empty split

        for item_part in item_parts:
            # Each item goes until the next \item or end of block
            item_text = item_part.strip()
            # Remove trailing content after the item
            item_text = re.split(r'\\end\{cvitems\}', item_text)[0].strip()

            if item_text:
                item_text = clean_latex_text(item_text)
                if item_text and '[' not in item_text:  # Skip placeholders
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
    with open(cv_resume_path, 'r', encoding='utf-8') as f:
        content = f.read()

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
