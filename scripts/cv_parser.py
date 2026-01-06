#!/usr/bin/env python3
"""
CV Parser - Extracts structured data from LaTeX CV files into JSON library
Parses .tex files from cv/ subdirectories to build a searchable experience library
"""

import re
import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set, Union
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cv_utils.regex_parsing import normalize_company, normalize_dates  # noqa: E402
from cv_utils.file_io import read_text_file_safe  # noqa: E402


class CVParser:
    def __init__(self, cv_base_path: Union[str, Path] = "./_content"):
        self.cv_base_path = Path(cv_base_path)
        self.jobs: List[Dict[str, Any]] = []  # Will be list of job experiences
        self.skills_by_job: Dict[str, List[str]] = {}  # Skills organized by job context
        self.education: List[Dict[str, Any]] = []  # Education entries
        self.certificates: List[Dict[str, str]] = []  # Certificates
        self.honors: List[Dict[str, str]] = []  # Honors and awards
        self.committees: List[Dict[str, str]] = []  # Committee memberships
        self.writing: List[Dict[str, Any]] = []  # Writing projects
        self.presentations: List[Dict[str, Any]] = []  # Presentations
        self.extracurricular: List[Dict[str, Any]] = []  # Extracurricular activities
        self.template_hashes = self._load_template_hashes()

    def _normalize_for_hash(self, content: str) -> str:
        """Normalize content for consistent hashing (handles line endings, whitespace)"""
        # Normalize line endings to \n
        normalized = content.replace('\r\n', '\n').replace('\r', '\n')
        # Normalize multiple spaces/tabs to single space
        normalized = re.sub(r'[ \t]+', ' ', normalized)
        # Remove trailing whitespace from each line
        normalized = '\n'.join(line.rstrip() for line in normalized.split('\n'))
        # Remove leading/trailing whitespace from entire content
        return normalized.strip()

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of normalized file content"""
        if not file_path.exists():
            return ""
        content = file_path.read_text(encoding='utf-8')
        normalized = self._normalize_for_hash(content)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _load_template_hashes(self) -> Set[str]:
        """Load hashes of all template files to exclude from parsing"""
        template_hashes = set()
        template_dir = self.cv_base_path / "_template"

        if template_dir.exists():
            for template_file in template_dir.glob("*.tex"):
                file_hash = self._compute_file_hash(template_file)
                if file_hash:
                    template_hashes.add(file_hash)

        return template_hashes

    def _clean_text(self, text: str) -> str:
        """Clean LaTeX formatting from text"""
        cleaned = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
        cleaned = re.sub(r'\\&', '&', cleaned)
        cleaned = re.sub(r'\\%', '%', cleaned)
        cleaned = re.sub(r'\\\$', '$', cleaned)
        cleaned = re.sub(r'\\end\{cvitems\}', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _normalize_company(self, company: str) -> str:
        """Normalize company names for matching"""
        return normalize_company(company)

    def _normalize_dates(self, dates: str) -> str:
        """Normalize date formats for matching"""
        return normalize_dates(dates)

    def _extract_balanced_braces(self, text: str, start_pos: int) -> str:
        """Extract content within balanced braces starting at start_pos"""
        if start_pos >= len(text) or text[start_pos] != '{':
            return ""

        brace_count = 0
        result = ""

        for i in range(start_pos, len(text)):
            char = text[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return result
            elif brace_count > 0:
                result += char

        return result

    def parse_experience_tex(self, content: str) -> List[Dict[str, Any]]:
        """Parse experience.tex file to extract job entries"""
        jobs = []

        # Find all \cventry positions
        # Pattern matches \cventry followed by an optional '%' (authors sometimes use
        # "\cventry%" to comment the macro) and optional whitespace/newline.
        # Accept both "\cventry" and "\cventry%" styles.
        cventry_pattern = r'\\cventry\s*%?\s*'
        matches = list(re.finditer(cventry_pattern, content))

        for match in matches:
            pos = match.end()

            # Extract 5 brace-delimited arguments
            args = []
            for _ in range(5):
                # Skip whitespace
                while pos < len(content) and content[pos] in ' \t\n':
                    pos += 1

                if pos >= len(content) or content[pos] != '{':
                    break

                arg = self._extract_balanced_braces(content, pos)
                args.append(arg.strip())

                # Move past the closing brace
                pos += len(arg) + 2  # +2 for { and }

            if len(args) >= 5:
                role, company, location, dates, items_block = args[:5]

                # Extract bullet points
                achievements = []
                item_pattern = r'\\item\s+(.*?)(?=\\item|\\end|$)'
                items = re.findall(item_pattern, items_block, re.DOTALL)

                for item in items:
                    cleaned = self._clean_text(item)
                    if cleaned and len(cleaned) > 10:
                        achievements.append(cleaned)

                job = {
                    "titles": [self._clean_text(role)],
                    "company": self._normalize_company(self._clean_text(company)),
                    "location": self._clean_text(location),
                    "dates": self._clean_text(dates),
                    "achievements": achievements
                }

                jobs.append(job)

        return jobs

    def parse_skills_tex(self, content: str) -> Dict[str, List[str]]:
        """Parse skills.tex file to extract skill categories"""
        skills = {}

        # Match \cvskill entries
        pattern = r'\\cvskill\s*\{([^}]*)\}\s*\{([^}]*)\}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            category = self._clean_text(match.group(1))
            skills_list = self._clean_text(match.group(2))

            # Split by commas and clean
            skill_items = [s.strip() for s in skills_list.split(',') if s.strip()]
            if skill_items:
                skills[category] = skill_items

        return skills

    def parse_cvhonors_tex(self, content: str) -> List[Dict[str, str]]:
        """Parse cvhonors environment (certificates, honors, committees).

        Uses \\cvhonor{name}{organization}{location}{date}
        """
        honors_list = []

        # Match \cvhonor entries
        pattern = r'\\cvhonor\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            name = self._clean_text(match.group(1))
            organization = self._clean_text(match.group(2))
            location = self._clean_text(match.group(3))
            date = self._clean_text(match.group(4))

            # Skip template placeholders
            if '[' in name or not name:
                continue

            honors_list.append({
                'name': name,
                'organization': organization,
                'location': location,
                'date': date
            })

        return honors_list

    def parse_cventries_generic_tex(self, content: str) -> List[Dict[str, Any]]:
        """Parse generic cventries environment (education, writing, presentations, extracurricular).

        Uses \\cventry{title}{org}{location}{date}{items}
        Same structure as experience.
        """
        entries = []

        # Find all \cventry positions
        # Pattern matches \cventry followed by an optional '%' and optional whitespace/newline
        # This mirrors the experience parser so generic entries are also detected when
        # the macro is immediately followed by '%'.
        cventry_pattern = r'\\cventry\s*%?\s*'
        matches = list(re.finditer(cventry_pattern, content))

        for match in matches:
            pos = match.end()

            # Extract 5 brace-delimited arguments
            args = []
            for _ in range(5):
                # Skip whitespace
                while pos < len(content) and content[pos] in ' \t\n':
                    pos += 1

                if pos >= len(content) or content[pos] != '{':
                    break

                arg = self._extract_balanced_braces(content, pos)
                args.append(arg.strip())

                # Move past the closing brace
                pos += len(arg) + 2  # +2 for { and }

            if len(args) >= 5:
                title, organization, location, dates, items_block = args[:5]

                # Skip template placeholders
                if '[' in title or not title:
                    continue

                # Extract bullet points
                achievements = []
                item_pattern = r'\\item\s+(.*?)(?=\\item|\\end|$)'
                items = re.findall(item_pattern, items_block, re.DOTALL)

                for item in items:
                    cleaned = self._clean_text(item)
                    if cleaned and len(cleaned) > 10 and '[' not in cleaned:
                        achievements.append(cleaned)

                entry = {
                    "title": self._clean_text(title),
                    "organization": self._clean_text(organization),
                    "location": self._clean_text(location),
                    "dates": self._clean_text(dates),
                    "items": achievements
                }

                entries.append(entry)

        return entries

    def parse_cv_directory(self, cv_dir: Path):
        """Parse all sections from a CV directory"""
        # Parse experience.tex
        exp_file = cv_dir / "experience.tex"
        file_hash = self._compute_file_hash(exp_file)
        if file_hash and file_hash not in self.template_hashes:
            content = read_text_file_safe(exp_file)
            if content:
                jobs = self.parse_experience_tex(content)
                self.jobs.extend(jobs)
        elif file_hash:
            print(f"  Skipping template file: {exp_file.relative_to(self.cv_base_path)}")

        # Parse skills.tex
        skills_file = cv_dir / "skills.tex"
        if skills_file.exists():
            file_hash = self._compute_file_hash(skills_file)
            if file_hash not in self.template_hashes:
                content = skills_file.read_text(encoding='utf-8')
                skills = self.parse_skills_tex(content)
                if skills:
                    self.skills_by_job[cv_dir.name] = skills
            else:
                print(f"  Skipping template file: {skills_file.relative_to(self.cv_base_path)}")

        # Parse education.tex
        edu_file = cv_dir / "education.tex"
        if edu_file.exists():
            file_hash = self._compute_file_hash(edu_file)
            if file_hash not in self.template_hashes:
                content = edu_file.read_text(encoding='utf-8')
                education = self.parse_cventries_generic_tex(content)
                self.education.extend(education)
            else:
                print(f"  Skipping template file: {edu_file.relative_to(self.cv_base_path)}")

        # Parse certificates.tex
        cert_file = cv_dir / "certificates.tex"
        if cert_file.exists():
            file_hash = self._compute_file_hash(cert_file)
            if file_hash not in self.template_hashes:
                content = cert_file.read_text(encoding='utf-8')
                certificates = self.parse_cvhonors_tex(content)
                self.certificates.extend(certificates)
            else:
                print(f"  Skipping template file: {cert_file.relative_to(self.cv_base_path)}")

        # Parse honors.tex
        honors_file = cv_dir / "honors.tex"
        if honors_file.exists():
            file_hash = self._compute_file_hash(honors_file)
            if file_hash not in self.template_hashes:
                content = honors_file.read_text(encoding='utf-8')
                honors = self.parse_cvhonors_tex(content)
                self.honors.extend(honors)
            else:
                print(f"  Skipping template file: {honors_file.relative_to(self.cv_base_path)}")

        # Parse committees.tex
        committees_file = cv_dir / "committees.tex"
        if committees_file.exists():
            file_hash = self._compute_file_hash(committees_file)
            if file_hash not in self.template_hashes:
                content = committees_file.read_text(encoding='utf-8')
                committees = self.parse_cvhonors_tex(content)
                self.committees.extend(committees)
            else:
                print(f"  Skipping template file: {committees_file.relative_to(self.cv_base_path)}")

        # Parse writing.tex
        writing_file = cv_dir / "writing.tex"
        if writing_file.exists():
            file_hash = self._compute_file_hash(writing_file)
            if file_hash not in self.template_hashes:
                content = writing_file.read_text(encoding='utf-8')
                writing = self.parse_cventries_generic_tex(content)
                self.writing.extend(writing)
            else:
                print(f"  Skipping template file: {writing_file.relative_to(self.cv_base_path)}")

        # Parse presentation.tex
        pres_file = cv_dir / "presentation.tex"
        if pres_file.exists():
            file_hash = self._compute_file_hash(pres_file)
            if file_hash not in self.template_hashes:
                content = pres_file.read_text(encoding='utf-8')
                presentations = self.parse_cventries_generic_tex(content)
                self.presentations.extend(presentations)
            else:
                print(f"  Skipping template file: {pres_file.relative_to(self.cv_base_path)}")

        # Parse extracurricular.tex
        extra_file = cv_dir / "extracurricular.tex"
        if extra_file.exists():
            file_hash = self._compute_file_hash(extra_file)
            if file_hash not in self.template_hashes:
                content = extra_file.read_text(encoding='utf-8')
                extracurricular = self.parse_cventries_generic_tex(content)
                self.extracurricular.extend(extracurricular)
            else:
                print(f"  Skipping template file: {extra_file.relative_to(self.cv_base_path)}")

    def parse_all_cvs(self):
        """Parse all CV directories"""
        for cv_dir in self.cv_base_path.iterdir():
            if cv_dir.is_dir() and not cv_dir.name.startswith('.') and not cv_dir.name.startswith('_'):
                print(f"Parsing {cv_dir.name}...")
                self.parse_cv_directory(cv_dir)

    def merge_jobs(self):
        """Merge jobs by company and overlapping years"""
        # Group by normalized company name
        company_groups = defaultdict(list)
        for job in self.jobs:
            company_groups[job["company"]].append(job)

        merged = []
        for company_jobs in company_groups.values():
            # Further group by date ranges
            date_groups = defaultdict(list)
            for job in company_jobs:
                # Normalize dates for grouping
                dates_key = self._normalize_dates(job["dates"])
                date_groups[dates_key].append(job)

            # Merge jobs with same company and dates
            for date_jobs in date_groups.values():
                if len(date_jobs) == 1:
                    merged.append(date_jobs[0])
                else:
                    # Merge multiple variants
                    base_job = date_jobs[0].copy()
                    all_titles = []
                    all_achievements = []

                    for job in date_jobs:
                        all_titles.extend(job["titles"])
                        all_achievements.extend(job["achievements"])

                    # Deduplicate while preserving order
                    base_job["titles"] = list(dict.fromkeys(all_titles))
                    base_job["achievements"] = list(dict.fromkeys(all_achievements))

                    merged.append(base_job)

        # Sort by date (most recent first)
        self.jobs = sorted(merged, key=lambda x: x["dates"], reverse=True)

    def export_to_json(self, output_dir: Union[str, Path] = "./cv_library") -> None:
        """Export parsed data to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        exports = []

        # Export job history
        if self.jobs:
            with open(output_path / "experience_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            exports.append(f"experience_library.json ({len(self.jobs)} jobs)")

        # Export skills by job context
        if self.skills_by_job:
            with open(output_path / "skills_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.skills_by_job, f, indent=2, ensure_ascii=False)
            exports.append(f"skills_library.json ({len(self.skills_by_job)} job contexts)")

        # Export education
        if self.education:
            with open(output_path / "education_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.education, f, indent=2, ensure_ascii=False)
            exports.append(f"education_library.json ({len(self.education)} entries)")

        # Export certificates
        if self.certificates:
            with open(output_path / "certificates_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.certificates, f, indent=2, ensure_ascii=False)
            exports.append(f"certificates_library.json ({len(self.certificates)} certificates)")

        # Export honors
        if self.honors:
            with open(output_path / "honors_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.honors, f, indent=2, ensure_ascii=False)
            exports.append(f"honors_library.json ({len(self.honors)} honors)")

        # Export committees
        if self.committees:
            with open(output_path / "committees_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.committees, f, indent=2, ensure_ascii=False)
            exports.append(f"committees_library.json ({len(self.committees)} committees)")

        # Export writing
        if self.writing:
            with open(output_path / "writing_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.writing, f, indent=2, ensure_ascii=False)
            exports.append(f"writing_library.json ({len(self.writing)} writing projects)")

        # Export presentations
        if self.presentations:
            with open(output_path / "presentations_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.presentations, f, indent=2, ensure_ascii=False)
            exports.append(f"presentations_library.json ({len(self.presentations)} presentations)")

        # Export extracurricular
        if self.extracurricular:
            with open(output_path / "extracurricular_library.json", 'w', encoding='utf-8') as f:
                json.dump(self.extracurricular, f, indent=2, ensure_ascii=False)
            exports.append(f"extracurricular_library.json ({len(self.extracurricular)} activities)")

        print(f"\n✓ Exported to {output_dir}/")
        for export in exports:
            print(f"  - {export}")


def main() -> None:
    """Main entry point for CV parser."""
    parser = CVParser()

    print("Parsing CV files...")
    parser.parse_all_cvs()

    print("\nMerging jobs by company/year...")
    parser.merge_jobs()

    print("\nExporting to JSON...")
    parser.export_to_json()

    print("\n✓ Done! CV library ready for LLM consumption.")


if __name__ == "__main__":
    main()
