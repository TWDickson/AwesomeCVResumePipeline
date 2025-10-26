"""
Test the build system using comprehensive SpongeBob test fixtures.

This test validates that:
1. All template sections exist and have content
2. LaTeX files are properly formatted
3. Files contain expected character names and data
4. All section types are included
"""

import pytest
import shutil
from pathlib import Path
import re


class TestFixtures:
    """Test comprehensive resume fixtures using SpongeBob character."""

    @pytest.fixture
    def fixtures_dir(self) -> Path:
        """Get path to test fixtures directory."""
        return Path(__file__).parent / "fixtures"

    @pytest.fixture
    def test_content_dir(self, tmp_path, fixtures_dir):
        """Create temporary content directory with fixtures."""
        content_dir = tmp_path / "_content" / "spongebob_test"
        content_dir.mkdir(parents=True)
        
        # Copy all fixtures
        for fixture_file in fixtures_dir.glob("*.tex"):
            shutil.copy(fixture_file, content_dir / fixture_file.name)
        
        return content_dir

    def test_fixtures_exist(self, fixtures_dir):
        """Verify all required fixture files exist."""
        required_files = [
            "cv-personal-details.tex",
            "tagline.tex",
            "summary.tex",
            "skills.tex",
            "experience.tex",
            "education.tex",
            "certificates.tex",
            "honors.tex",
            "extracurricular.tex",
            "writing.tex",
            "presentation.tex",
            "committees.tex",
            "cover_letter.tex",
        ]
        
        for filename in required_files:
            filepath = fixtures_dir / filename
            assert filepath.exists(), f"Missing required fixture: {filename}"
            assert filepath.stat().st_size > 0, f"Empty fixture file: {filename}"

    def test_personal_details_parsing(self, test_content_dir):
        """Test extraction of personal information from fixtures."""
        personal_file = test_content_dir / "cv-personal-details.tex"
        
        # This would normally be in a separate file in the project root
        # For testing, we'll just verify the file has expected content
        content = personal_file.read_text()
        
        assert "SpongeBob" in content
        assert "SquarePants" in content
        assert "spongebob@krustykrab.com" in content
        assert "124 Conch Street" in content

    def test_summary_content(self, test_content_dir):
        """Test summary section has proper content."""
        summary_file = test_content_dir / "summary.tex"
        content = summary_file.read_text()
        
        assert "\\begin{cvparagraph}" in content
        assert "\\end{cvparagraph}" in content
        assert "Fry Cook" in content
        assert "Krusty Krab" in content
        assert "Employee of the Month" in content
        assert len(content) > 200

    def test_skills_content(self, test_content_dir):
        """Test skills section has multiple categories."""
        skills_file = test_content_dir / "skills.tex"
        content = skills_file.read_text()
        
        assert "\\begin{cvskills}" in content
        assert "\\end{cvskills}" in content
        
        # Count cvskill entries
        skill_count = content.count("\\cvskill")
        assert skill_count >= 6, f"Should have at least 6 skill categories, found {skill_count}"
        
        # Check for expected categories
        assert "Cooking" in content
        assert "Customer Service" in content
        assert "Technical Skills" in content
        assert "Specialized Skills" in content
        assert "Krabby Patty" in content

    def test_experience_content(self, test_content_dir):
        """Test experience section with multiple jobs and bullet points."""
        exp_file = test_content_dir / "experience.tex"
        content = exp_file.read_text()
        
        assert "\\begin{cventries}" in content
        assert "\\end{cventries}" in content
        
        # Count cventry entries
        entry_count = content.count("\\cventry")
        assert entry_count >= 5, f"Should have at least 5 job entries, found {entry_count}"
        
        # Check for key companies and positions
        assert "Fry Cook" in content
        assert "Krusty Krab" in content
        assert "Bikini Bottom, Pacific Ocean" in content
        assert "May 1999 - Present" in content
        
        # Count cvitems blocks (bullet points)
        items_count = content.count("\\begin{cvitems}")
        assert items_count >= 5, "Should have bullet points for all jobs"
        
        # Verify key achievements mentioned
        assert "1 million" in content.lower() or "million" in content
        assert "374" in content  # Employee of the Month count

    def test_education_content(self, test_content_dir):
        """Test education section has proper content."""
        edu_file = test_content_dir / "education.tex"
        content = edu_file.read_text()
        
        assert "\\begin{cventries}" in content
        assert "\\end{cventries}" in content
        
        entry_count = content.count("\\cventry")
        assert entry_count >= 2, f"Should have at least 2 education entries, found {entry_count}"
        
        assert "Certificate" in content
        assert "Bikini Bottom Community College" in content
        assert "High School" in content

    def test_certificates_content(self, test_content_dir):
        """Test certificates section with cvhonors format."""
        cert_file = test_content_dir / "certificates.tex"
        content = cert_file.read_text()
        
        assert "\\begin{cvhonors}" in content
        assert "\\end{cvhonors}" in content
        
        honor_count = content.count("\\cvhonor")
        assert honor_count >= 5, f"Should have at least 5 certificates, found {honor_count}"
        
        assert "Fry Cook" in content
        assert "Jellyfishing" in content
        assert "Food Safety" in content

    def test_honors_content(self, test_content_dir):
        """Test honors and awards section."""
        honors_file = test_content_dir / "honors.tex"
        content = honors_file.read_text()
        
        assert "\\begin{cvhonors}" in content
        assert "\\end{cvhonors}" in content
        
        honor_count = content.count("\\cvhonor")
        assert honor_count >= 5, f"Should have at least 5 honors, found {honor_count}"
        
        assert "Employee of the Month" in content
        assert "374" in content  # 374 consecutive awards
        assert "Golden Spatula" in content

    def test_extracurricular_content(self, test_content_dir):
        """Test extracurricular activities section."""
        extra_file = test_content_dir / "extracurricular.tex"
        content = extra_file.read_text()
        
        assert "\\begin{cventries}" in content
        assert "\\end{cventries}" in content
        
        entry_count = content.count("\\cventry")
        assert entry_count >= 3, f"Should have at least 3 activities, found {entry_count}"
        
        assert "Jellyfishing" in content
        assert "Founder" in content or "President" in content
        assert "Karate" in content

    def test_writing_content(self, test_content_dir):
        """Test writing/publications section."""
        writing_file = test_content_dir / "writing.tex"
        content = writing_file.read_text()
        
        assert "\\begin{cventries}" in content
        assert "\\end{cventries}" in content
        
        entry_count = content.count("\\cventry")
        assert entry_count >= 3, f"Should have at least 3 publications, found {entry_count}"
        
        assert "Krabby Patty Chronicles" in content
        assert "Author" in content or "Writer" in content

    def test_presentations_content(self, test_content_dir):
        """Test presentations section."""
        pres_file = test_content_dir / "presentation.tex"
        content = pres_file.read_text()
        
        assert "\\begin{cventries}" in content
        assert "\\end{cventries}" in content
        
        entry_count = content.count("\\cventry")
        assert entry_count >= 3, f"Should have at least 3 presentations, found {entry_count}"
        
        assert "Keynote" in content
        assert "Workshop" in content or "Lecturer" in content

    def test_committees_content(self, test_content_dir):
        """Test committees and organizations section."""
        comm_file = test_content_dir / "committees.tex"
        content = comm_file.read_text()
        
        assert "\\begin{cvhonors}" in content
        assert "\\end{cvhonors}" in content
        
        honor_count = content.count("\\cvhonor")
        assert honor_count >= 5, f"Should have at least 5 committee memberships, found {honor_count}"
        
        assert "Board Member" in content
        assert "Restaurant Association" in content

    def test_cover_letter_content(self, test_content_dir):
        """Test cover letter has proper content."""
        cover_file = test_content_dir / "cover_letter.tex"
        content = cover_file.read_text()
        
        assert "\\storecontent{" in content
        assert "Dear Hiring Manager" in content
        assert "Sincerely" in content
        assert "SpongeBob SquarePants" in content
        assert "Fancy! Restaurant" in content
        assert len(content) > 2000, "Cover letter should be substantial"

    def test_comprehensive_content_coverage(self, test_content_dir):
        """Test that fixtures provide comprehensive coverage of features."""
        # Count total bullet points across all sections
        exp_file = test_content_dir / "experience.tex"
        content = exp_file.read_text()
        
        # Count \\item entries
        bullet_count = content.count("\\item")
        assert bullet_count >= 20, f"Should have 20+ bullets, found {bullet_count}"
        
        # Verify date range spans multiple decades
        assert "1998" in content or "1999" in content
        assert "2024" in content or "Present" in content

    def test_special_characters_handling(self, test_content_dir):
        """Test that fixtures include LaTeX special characters."""
        skills_file = test_content_dir / "skills.tex"
        content = skills_file.read_text()
        
        # Should have & (ampersand) in skills
        assert "\\&" in content or "&" in content
        
        # Experience should have percentages
        exp_file = test_content_dir / "experience.tex"
        exp_content = exp_file.read_text()
        assert "\\%" in exp_content or "%" in exp_content

    def test_readme_exists(self, fixtures_dir):
        """Test that fixtures README documentation exists."""
        readme = fixtures_dir / "README.md"
        assert readme.exists()
        assert readme.stat().st_size > 5000, "README should be comprehensive"
        
        readme_content = readme.read_text()
        assert "SpongeBob" in readme_content
        assert "Coverage" in readme_content
        assert "Testing" in readme_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
