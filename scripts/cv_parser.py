#!/usr/bin/env python3
"""
CV Parser - Extracts structured data from LaTeX CV files into JSON library
Parses .tex files from cv/ subdirectories to build a searchable experience library
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Set, Union
from collections import defaultdict


class CVParser:
    def __init__(self, cv_base_path: Union[str, Path] = "./_content"):
        self.cv_base_path = Path(cv_base_path)
        self.jobs: List[Dict[str, Any]] = []  # Will be list of job experiences
        self.skills_by_job: Dict[str, List[str]] = {}  # Skills organized by job context
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
        # Normalize dashes (--- to -)
        normalized = re.sub(r'\s*-{2,}\s*', ' - ', company)
        # Remove variations like "Ministry of the"
        normalized = re.sub(r'\s+-\s+Ministry of the\s+', ' - ', normalized, flags=re.IGNORECASE)
        return normalized.strip()

    def _normalize_dates(self, dates: str) -> str:
        """Normalize date formats for matching"""
        # Normalize dashes
        normalized = re.sub(r'\s*-{2,}\s*', ' - ', dates)
        # Normalize "Present" vs actual year
        normalized = re.sub(r'Present', '2024', normalized, flags=re.IGNORECASE)
        # Remove all whitespace for comparison
        normalized = re.sub(r'\s+', '', normalized)
        return normalized

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
        cventry_pattern = r'\\cventry\s*%?[^\n]*\n?\s*'
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

    def parse_cv_directory(self, cv_dir: Path):
        """Parse experience and skills from a CV directory"""
        # Parse experience.tex
        exp_file = cv_dir / "experience.tex"
        if exp_file.exists():
            # Skip if file matches template hash
            file_hash = self._compute_file_hash(exp_file)
            if file_hash not in self.template_hashes:
                content = exp_file.read_text(encoding='utf-8')
                jobs = self.parse_experience_tex(content)
                self.jobs.extend(jobs)
            else:
                print(f"  Skipping template file: {exp_file.relative_to(self.cv_base_path)}")

        # Parse skills.tex
        skills_file = cv_dir / "skills.tex"
        if skills_file.exists():
            # Skip if file matches template hash
            file_hash = self._compute_file_hash(skills_file)
            if file_hash not in self.template_hashes:
                content = skills_file.read_text(encoding='utf-8')
                skills = self.parse_skills_tex(content)
                if skills:
                    self.skills_by_job[cv_dir.name] = skills
            else:
                print(f"  Skipping template file: {skills_file.relative_to(self.cv_base_path)}")

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

        # Export job history
        with open(output_path / "experience_library.json", 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        # Export skills by job context
        with open(output_path / "skills_library.json", 'w', encoding='utf-8') as f:
            json.dump(self.skills_by_job, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Exported to {output_dir}/")
        print(f"  - experience_library.json ({len(self.jobs)} jobs)")
        print(f"  - skills_library.json ({len(self.skills_by_job)} job contexts)")


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
