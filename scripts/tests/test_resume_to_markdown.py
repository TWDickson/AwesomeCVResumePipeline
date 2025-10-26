#!/usr/bin/env python3
"""
Tests for resume_to_markdown.py
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_to_markdown import (
    clean_latex_text,
    extract_personal_info,
    extract_tagline,
    extract_summary,
    extract_skills,
    extract_experience,
    extract_cvhonors,
    extract_cventries_generic,
    extract_section_order
)


class TestCleanLatexText:
    """Test LaTeX text cleaning."""

    def test_bold_conversion(self):
        assert clean_latex_text(r'\textbf{Bold Text}') == '**Bold Text**'

    def test_italic_conversion(self):
        assert clean_latex_text(r'\textit{Italic}') == '*Italic*'

    def test_special_characters(self):
        result = clean_latex_text(r'\& \%')
        assert '&' in result
        assert '%' in result

    def test_whitespace_normalization(self):
        assert clean_latex_text('Multiple   spaces') == 'Multiple spaces'

    def test_escaped_percent_with_comment(self):
        """Test that escaped % is preserved even when followed by comment."""
        result = clean_latex_text(r'100\% availability % This is a comment')
        assert '100% availability' in result
        assert 'comment' not in result.lower()

    def test_escaped_percent_without_comment(self):
        """Test that escaped % is converted properly."""
        result = clean_latex_text(r'Reduced by 60\% through improvements')
        assert '60% through' in result

    def test_nested_braces_with_spacing(self):
        """Test nested braces with spacing commands are removed properly."""
        result = clean_latex_text(r'Data Engineer{\enskip\cdotp\enskip}Software Engineering')
        assert result == 'Data Engineer · Software Engineering'

    def test_multiple_spacing_separators(self):
        """Test multiple spacing separators in sequence."""
        result = clean_latex_text(
            r'Data Engineer{\enskip\cdotp\enskip}Software Engineering{\enskip\cdotp\enskip}Technical Leadership'
        )
        assert result == 'Data Engineer · Software Engineering · Technical Leadership'

    def test_cdotp_conversion(self):
        """Test that \cdotp is converted to middle dot."""
        result = clean_latex_text(r'A\cdotp B')
        assert '·' in result

    def test_escaped_ampersand(self):
        """Test that \& is converted to &."""
        result = clean_latex_text(r'Research \& Development')
        assert 'Research & Development' == result

    def test_escaped_underscore(self):
        """Test that \_ is converted to _."""
        result = clean_latex_text(r'test\_function')
        assert 'test_function' == result

    def test_escaped_dollar(self):
        """Test that \$ is converted to $."""
        result = clean_latex_text(r'\$100 million')
        assert '$100 million' == result

    def test_comment_removal(self):
        """Test that LaTeX comments are removed."""
        result = clean_latex_text('Some text % This is a comment\nMore text')
        assert 'comment' not in result.lower()
        assert 'Some text' in result
        assert 'More text' in result


class TestExtractCVHonors:
    """Test cvhonors parser for certificates, honors, committees."""

    def test_simple_honor(self, tmp_path):
        """Test parsing a simple honor entry."""
        content = r"""\cvsection{Certificates}
\begin{cvhonors}
  \cvhonor{AWS Solutions Architect}{Amazon Web Services}{ID: ABC123}{2023}
\end{cvhonors}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cvhonors(file_path)

        assert len(result) == 1
        assert result[0]['name'] == 'AWS Solutions Architect'
        assert result[0]['organization'] == 'Amazon Web Services'
        assert result[0]['location'] == 'ID: ABC123'
        assert result[0]['date'] == '2023'

    def test_template_placeholder_filtering(self, tmp_path):
        """Test that template placeholders are filtered out."""
        content = r"""
\begin{cvhonors}
  \cvhonor
    {[Certification Name]} % Name
    {[Issuing Organization]} % Issuer
    {[Credential ID or leave empty]} % Credential ID
    {[Year or Date Range]} % Date
\end{cvhonors}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cvhonors(file_path)

        assert len(result) == 0  # Should filter out template

    def test_honors_with_subsections(self, tmp_path):
        """Test parsing honors with subsections."""
        content = r"""\cvsection{Honors \& Awards}
\cvsubsection{International Awards}
\begin{cvhonors}
  \cvhonor{First Place}{Global Hackathon}{San Francisco, CA}{2023}
\end{cvhonors}

\cvsubsection{Academic Honors}
\begin{cvhonors}
  \cvhonor{Dean's List}{University of Example}{}{2020-2023}
\end{cvhonors}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cvhonors(file_path)

        assert len(result) == 2
        assert result[0]['subsection'] == 'International Awards'
        assert result[0]['name'] == 'First Place'
        assert result[1]['subsection'] == 'Academic Honors'
        assert result[1]['name'] == "Dean's List"


class TestExtractCVEntriesGeneric:
    """Test generic cventries parser for education, writing, presentations, etc."""

    def test_education_entry(self, tmp_path):
        """Test parsing an education entry."""
        content = r"""
\cvsection{Education}
\begin{cventries}
  \cventry
    {B.S. in Computer Science} % Degree
    {University of Example} % Institution
    {Cambridge, MA} % Location
    {Sept. 2015 - May 2019} % Date(s)
    {
      \begin{cvitems}
        \item {Graduated with Honors (GPA: 3.9/4.0)}
        \item {Relevant coursework: Machine Learning, Data Structures, Algorithms}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cventries_generic(file_path)

        assert len(result) == 1
        assert result[0]['title'] == 'B.S. in Computer Science'
        assert result[0]['organization'] == 'University of Example'
        assert result[0]['location'] == 'Cambridge, MA'
        assert result[0]['dates'] == 'Sept. 2015 - May 2019'
        assert len(result[0]['items']) == 2
        assert 'Graduated with Honors' in result[0]['items'][0]

    def test_writing_entry(self, tmp_path):
        """Test parsing a writing entry."""
        content = r"""
\cvsection{Writing}
\begin{cventries}
  \cventry
    {Author} % Role
    {Tech Blog} % Title
    {Medium} % Platform
    {2020 - PRESENT} % Date(s)
    {
      \begin{cvitems}
        \item {Published 50+ technical articles on cloud architecture and DevOps}
        \item {10K+ monthly readers and 500+ followers}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cventries_generic(file_path)

        assert len(result) == 1
        assert result[0]['title'] == 'Author'
        assert result[0]['organization'] == 'Tech Blog'
        assert result[0]['location'] == 'Medium'
        assert len(result[0]['items']) == 2

    def test_template_filtering(self, tmp_path):
        """Test that template entries are filtered."""
        content = r"""
\begin{cventries}
  \cventry
    {[Your Role/Position]} % Role
    {[Organization Name]} % Organization
    {[City, State]} % Location
    {[Start - End]} % Date(s)
    {
      \begin{cvitems}
        \item {[Some description]}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "test.tex"
        file_path.write_text(content)

        result = extract_cventries_generic(file_path)

        assert len(result) == 0


class TestExtractSectionOrder:
    """Test section order extraction from cv-resume.tex."""

    def test_default_section_order(self, tmp_path):
        """Test extracting section order from cv-resume.tex."""
        content = r"""
\documentclass[11pt, letterpaper]{resume-pipeline}
\begin{document}
\makecvheader
\loadSections{summary, skills, experience}
\end{document}
"""
        file_path = tmp_path / "cv-resume.tex"
        file_path.write_text(content)

        result = extract_section_order(file_path)

        assert result == ['summary', 'skills', 'experience']

    def test_extended_section_order(self, tmp_path):
        """Test extracting extended section order."""
        content = r"""
\loadSections{summary, skills, experience, education, certificates, honors}
"""
        file_path = tmp_path / "cv-resume.tex"
        file_path.write_text(content)

        result = extract_section_order(file_path)

        assert result == ['summary', 'skills', 'experience', 'education', 'certificates', 'honors']

    def test_fallback_when_not_found(self, tmp_path):
        """Test fallback to default if loadSections not found."""
        content = r"""
\documentclass[11pt, letterpaper]{resume-pipeline}
\begin{document}
\makecvheader
\end{document}
"""
        file_path = tmp_path / "cv-resume.tex"
        file_path.write_text(content)

        result = extract_section_order(file_path)

        # Should return default
        assert result == ['summary', 'skills', 'experience']


class TestExtractPersonalInfo:
    """Test personal info extraction."""

    def test_complete_personal_info(self, tmp_path):
        """Test extracting complete personal information."""
        content = r"""
\name{John}{Doe}
\mobile{+1 555-1234}{(+1) 555-1234}
\email{john@example.com}
\homepage{johndoe.com}
\github{johndoe}
\linkedin{johndoe}
"""
        file_path = tmp_path / "cv-personal-details.tex"
        file_path.write_text(content)

        result = extract_personal_info(file_path)

        assert result['name'] == 'John Doe'
        assert result['mobile'] == '(+1) 555-1234'
        assert result['email'] == 'john@example.com'
        assert result['homepage'] == 'johndoe.com'
        assert result['github'] == 'johndoe'
        assert result['linkedin'] == 'johndoe'


class TestExtractTagline:
    """Test tagline extraction."""

    def test_valid_tagline(self, tmp_path):
        """Test extracting a valid tagline."""
        content = r"""
\position{Senior Software Engineer}
"""
        file_path = tmp_path / "tagline.tex"
        file_path.write_text(content)

        result = extract_tagline(file_path)

        assert result == 'Senior Software Engineer'

    def test_template_tagline(self, tmp_path):
        """Test that template placeholders return empty."""
        content = r"""
\position{[Your Title]}
"""
        file_path = tmp_path / "tagline.tex"
        file_path.write_text(content)

        result = extract_tagline(file_path)

        assert result == ''

    def test_tagline_with_nested_braces(self, tmp_path):
        """Test extracting tagline with nested braces and spacing commands.

        This was a bug where taglines like:
        Data Engineer{\enskip\cdotp\enskip}Software Engineering
        were being truncated at the first closing brace.
        """
        content = r"""
\position{Data Engineer{\enskip\cdotp\enskip}Software Engineering{\enskip\cdotp\enskip}Technical Leadership}
"""
        file_path = tmp_path / "tagline.tex"
        file_path.write_text(content)

        result = extract_tagline(file_path)

        assert result == 'Data Engineer · Software Engineering · Technical Leadership'

    def test_tagline_with_simple_separator(self, tmp_path):
        """Test tagline with simple separators."""
        content = r"""
\position{Backend Developer \cdotp Data Engineer}
"""
        file_path = tmp_path / "tagline.tex"
        file_path.write_text(content)

        result = extract_tagline(file_path)

        assert '·' in result
        assert 'Backend Developer' in result
        assert 'Data Engineer' in result


class TestExtractSummary:
    """Test summary extraction."""

    def test_summary_extraction(self, tmp_path):
        """Test extracting summary text."""
        content = r"""
\cvsection{Summary}
\begin{cvparagraph}
Experienced software engineer with 10+ years developing scalable applications.
Specializes in cloud architecture and DevOps practices.
\end{cvparagraph}
"""
        file_path = tmp_path / "summary.tex"
        file_path.write_text(content)

        result = extract_summary(file_path)

        assert 'Experienced software engineer' in result
        assert 'cloud architecture' in result


class TestExtractSkills:
    """Test skills extraction."""

    def test_multiple_skill_categories(self, tmp_path):
        """Test extracting multiple skill categories."""
        content = r"""
\cvsection{Skills}
\begin{cvskills}
  \cvskill
    {Languages} % Category
    {Python, JavaScript, Go, SQL} % Skills

  \cvskill
    {Cloud Platforms} % Category
    {AWS, Azure, Google Cloud} % Skills
\end{cvskills}
"""
        file_path = tmp_path / "skills.tex"
        file_path.write_text(content)

        result = extract_skills(file_path)

        assert len(result) == 2
        assert result[0]['category'] == 'Languages'
        assert 'Python' in result[0]['skills']
        assert result[1]['category'] == 'Cloud Platforms'
        assert 'AWS' in result[1]['skills']


class TestExtractExperience:
    """Test experience extraction."""

    def test_experience_entry(self, tmp_path):
        """Test extracting an experience entry."""
        content = r"""
\cvsection{Experience}
\begin{cventries}
  \cventry
    {Senior Software Engineer} % Job title
    {Tech Company Inc.} % Organization
    {San Francisco, CA} % Location
    {Jan. 2020 - PRESENT} % Date(s)
    {
      \begin{cvitems}
        \item {Led development of microservices architecture serving 1M+ users}
        \item {Reduced deployment time by 60\% through CI/CD improvements}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "experience.tex"
        file_path.write_text(content)

        result = extract_experience(file_path)

        assert len(result) == 1
        assert result[0]['title'] == 'Senior Software Engineer'
        assert result[0]['organization'] == 'Tech Company Inc.'
        assert result[0]['location'] == 'San Francisco, CA'
        assert len(result[0]['items']) == 2

    def test_experience_with_escaped_percent(self, tmp_path):
        """Test that escaped percent signs are preserved in experience items.

        This was a bug where text like '100\% availability' was being truncated
        because the comment removal regex was processing the escaped % as a comment marker.
        """
        content = r"""
\cvsection{Experience}
\begin{cventries}
  \cventry
    {Infrastructure Engineer} % Job title
    {Cloud Services Inc.} % Organization
    {Seattle, WA} % Location
    {Jan. 2018 - Dec. 2021} % Date(s)
    {
      \begin{cvitems}
        \item {Architected cloud infrastructure with 100\% availability, serving thousands of users}
        \item {Reduced costs by 60\% through optimization}
        \item {Achieved 99.99\% uptime SLA}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "experience.tex"
        file_path.write_text(content)

        result = extract_experience(file_path)

        assert len(result) == 1
        assert len(result[0]['items']) == 3

        # Check that all percent signs are preserved
        item_text = ' '.join(result[0]['items'])
        assert '100% availability' in item_text
        assert '60%' in item_text
        assert '99.99%' in item_text

    def test_experience_with_comments(self, tmp_path):
        """Test that LaTeX comments in experience items are removed."""
        content = r"""
\cvsection{Experience}
\begin{cventries}
  \cventry
    {Data Engineer} % Job title
    {Analytics Corp} % Organization
    {Austin, TX} % Location
    {2019 - 2022} % Date(s)
    {
      \begin{cvitems}
        \item {Built data pipelines % This is a comment about pipelines
        serving millions of requests daily}
      \end{cvitems}
    }
\end{cventries}
"""
        file_path = tmp_path / "experience.tex"
        file_path.write_text(content)

        result = extract_experience(file_path)

        assert len(result) == 1
        # Comments should be removed but real content preserved
        item_text = result[0]['items'][0]
        assert 'comment' not in item_text.lower()
        assert 'Built data pipelines' in item_text
        assert 'serving millions' in item_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
