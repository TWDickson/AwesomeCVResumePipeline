#!/usr/bin/env python3
"""
Tests for cv_parser.py
"""

import pytest
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_parser import CVParser


class TestCVParser:
    """Test the CVParser class."""

    @pytest.fixture
    def temp_cv_structure(self, tmp_path):
        """Create a temporary CV directory structure."""
        cv_base = tmp_path / "_content"
        cv_base.mkdir()

        # Create a template directory with template files
        template_dir = cv_base / "_template"
        template_dir.mkdir()

        # Create test version directory
        test_version = cv_base / "test_version"
        test_version.mkdir()

        return cv_base, template_dir, test_version

    def test_template_hash_loading(self, temp_cv_structure):
        """Test that template files are loaded and hashed."""
        cv_base, template_dir, test_version = temp_cv_structure

        # Create a template file
        template_exp = template_dir / "experience.tex"
        template_exp.write_text(r"""
\begin{cventries}
  \cventry
    {[Job Title]} % title
    {[Company]} % organization
    {[Location]} % location
    {[Dates]} % dates
    {
      \begin{cvitems}
        \item {[Description]}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)

        assert len(parser.template_hashes) > 0

    def test_parse_experience(self, temp_cv_structure):
        """Test parsing experience.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        # Create experience file with real content
        exp_file = test_version / "experience.tex"
        exp_file.write_text(r"""\begin{cventries}
  \cventry{Senior Engineer}{Tech Corp}{NYC, NY}{2020 - 2023}{
      \begin{cvitems}
        \item {Built scalable microservices architecture for serving millions of users}
        \item {Led team of 5 engineers and managed project deliverables}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.jobs) == 1
        assert parser.jobs[0]['titles'][0] == 'Senior Engineer'
        assert parser.jobs[0]['company'] == 'Tech Corp'
        assert len(parser.jobs[0]['achievements']) == 2

    def test_parse_skills(self, temp_cv_structure):
        """Test parsing skills.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        skills_file = test_version / "skills.tex"
        skills_file.write_text(r"""
\begin{cvskills}
  \cvskill
    {Languages}
    {Python, Go, JavaScript}

  \cvskill
    {Cloud}
    {AWS, GCP, Azure}
\end{cvskills}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert 'test_version' in parser.skills_by_job
        assert 'Languages' in parser.skills_by_job['test_version']
        assert 'Cloud' in parser.skills_by_job['test_version']

    def test_parse_education(self, temp_cv_structure):
        """Test parsing education.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        edu_file = test_version / "education.tex"
        edu_file.write_text(r"""\begin{cventries}
  \cventry{B.S. Computer Science}{University of Tech}{Boston, MA}{2015 - 2019}{
      \begin{cvitems}
        \item {Graduated with GPA: 3.9/4.0, Summa Cum Laude honors and distinction}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.education) == 1
        assert parser.education[0]['title'] == 'B.S. Computer Science'
        assert parser.education[0]['organization'] == 'University of Tech'

    def test_parse_certificates(self, temp_cv_structure):
        """Test parsing certificates.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        cert_file = test_version / "certificates.tex"
        cert_file.write_text(r"""
\begin{cvhonors}
  \cvhonor
    {AWS Solutions Architect}
    {Amazon Web Services}
    {ID: ABC123}
    {2023}
\end{cvhonors}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.certificates) == 1
        assert parser.certificates[0]['name'] == 'AWS Solutions Architect'

    def test_parse_honors(self, temp_cv_structure):
        """Test parsing honors.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        honors_file = test_version / "honors.tex"
        honors_file.write_text(r"""
\begin{cvhonors}
  \cvhonor
    {Employee of the Year}
    {Tech Corp}
    {}
    {2022}
\end{cvhonors}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.honors) == 1
        assert parser.honors[0]['name'] == 'Employee of the Year'

    def test_parse_committees(self, temp_cv_structure):
        """Test parsing committees.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        committees_file = test_version / "committees.tex"
        committees_file.write_text(r"""
\begin{cvhonors}
  \cvhonor
    {Technical Reviewer}
    {PyCon 2023}
    {Portland, OR}
    {2023}
\end{cvhonors}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.committees) == 1
        assert parser.committees[0]['name'] == 'Technical Reviewer'

    def test_parse_writing(self, temp_cv_structure):
        """Test parsing writing.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        writing_file = test_version / "writing.tex"
        writing_file.write_text(r"""\begin{cventries}
  \cventry{Author}{Tech Insights Blog}{Medium}{2020 - PRESENT}{
      \begin{cvitems}
        \item {Published 50+ articles on cloud architecture and modern software development practices}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.writing) == 1
        assert parser.writing[0]['title'] == 'Author'

    def test_parse_presentations(self, temp_cv_structure):
        """Test parsing presentation.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        pres_file = test_version / "presentation.tex"
        pres_file.write_text(r"""\begin{cventries}
  \cventry{Presenter for <Building Microservices>}{DevOps Summit 2023}{San Francisco, CA}{Mar 2023}{
      \begin{cvitems}
        \item {Presented to 500+ attendees on microservices architecture and design patterns}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.presentations) == 1
        assert 'Building Microservices' in parser.presentations[0]['title']

    def test_parse_extracurricular(self, temp_cv_structure):
        """Test parsing extracurricular.tex."""
        cv_base, template_dir, test_version = temp_cv_structure

        extra_file = test_version / "extracurricular.tex"
        extra_file.write_text(r"""\begin{cventries}
  \cventry{Volunteer}{Code for Good}{Boston, MA}{2019 - 2021}{
      \begin{cvitems}
        \item {Mentored underprivileged students in programming and computer science fundamentals}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        assert len(parser.extracurricular) == 1
        assert parser.extracurricular[0]['title'] == 'Volunteer'

    def test_template_file_skipping(self, temp_cv_structure):
        """Test that files matching template hashes are skipped."""
        cv_base, template_dir, test_version = temp_cv_structure

        # Create identical template and test files
        template_content = r"""
\begin{cventries}
  \cventry
    {[Job Title]}
    {[Company]}
    {[Location]}
    {[Dates]}
    {
      \begin{cvitems}
        \item {[Description]}
      \end{cvitems}
    }
\end{cventries}
"""
        template_exp = template_dir / "experience.tex"
        template_exp.write_text(template_content)

        test_exp = test_version / "experience.tex"
        test_exp.write_text(template_content)

        parser = CVParser(cv_base)
        parser.parse_cv_directory(test_version)

        # Should be empty because it matches template
        assert len(parser.jobs) == 0

    def test_merge_jobs_by_company(self, temp_cv_structure):
        """Test job merging by company and dates."""
        cv_base, template_dir, test_version = temp_cv_structure

        # Create two versions with overlapping experience
        version1 = cv_base / "version1"
        version1.mkdir()

        exp1 = version1 / "experience.tex"
        exp1.write_text(r"""\begin{cventries}
  \cventry{Senior Engineer}{Tech Corp}{NYC, NY}{2020 - 2023}{
      \begin{cvitems}
        \item {Built microservices architecture for cloud platform deployment}
      \end{cvitems}
    }
\end{cventries}
""")

        version2 = cv_base / "version2"
        version2.mkdir()

        exp2 = version2 / "experience.tex"
        exp2.write_text(r"""\begin{cventries}
  \cventry{Lead Engineer}{Tech Corp}{NYC, NY}{2020 - 2023}{
      \begin{cvitems}
        \item {Led team of engineers to deliver critical product features}
      \end{cvitems}
    }
\end{cventries}
""")

        parser = CVParser(cv_base)
        parser.parse_all_cvs()
        parser.merge_jobs()

        # Should merge into one job with both titles and achievements
        assert len(parser.jobs) == 1
        assert 'Senior Engineer' in parser.jobs[0]['titles']
        assert 'Lead Engineer' in parser.jobs[0]['titles']
        assert len(parser.jobs[0]['achievements']) == 2

    def test_export_to_json(self, temp_cv_structure, tmp_path):
        """Test JSON export functionality."""
        cv_base, template_dir, test_version = temp_cv_structure

        # Create files with content
        exp_file = test_version / "experience.tex"
        exp_file.write_text(r"""\begin{cventries}
  \cventry{Engineer}{Company}{NYC, NY}{2020 - 2023}{
      \begin{cvitems}
        \item {Did engineering things to build software systems and solve problems}
      \end{cvitems}
    }
\end{cventries}
""")

        skills_file = test_version / "skills.tex"
        skills_file.write_text(r"""\begin{cvskills}
  \cvskill{Languages}{Python}
\end{cvskills}
""")

        parser = CVParser(cv_base)
        parser.parse_all_cvs()

        output_dir = tmp_path / "output"
        parser.export_to_json(output_dir)

        # Check that files were created
        assert (output_dir / "experience_library.json").exists()
        assert (output_dir / "skills_library.json").exists()

        # Verify content
        with open(output_dir / "experience_library.json", 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['titles'][0] == 'Engineer'


class TestCleanText:
    """Test the _clean_text method."""

    def test_clean_text(self, tmp_path):
        cv_base = tmp_path / "_content"
        cv_base.mkdir()
        parser = CVParser(cv_base)

        text = r'\textbf{Bold} and \& special \% chars'
        result = parser._clean_text(text)

        assert 'Bold' in result
        assert '&' in result
        assert '%' in result


class TestNormalization:
    """Test normalization methods."""

    def test_normalize_company(self, tmp_path):
        cv_base = tmp_path / "_content"
        cv_base.mkdir()
        parser = CVParser(cv_base)

        # Test dash normalization
        result = parser._normalize_company('Company --- Subsidiary')
        assert result == 'Company - Subsidiary'

    def test_normalize_dates(self, tmp_path):
        cv_base = tmp_path / "_content"
        cv_base.mkdir()
        parser = CVParser(cv_base)

        # Test Present normalization
        result = parser._normalize_dates('2020 -- Present')
        assert '2024' in result  # Present should become 2024

        # Test whitespace removal
        result = parser._normalize_dates('Jan 2020 - Dec 2022')
        assert ' ' not in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
