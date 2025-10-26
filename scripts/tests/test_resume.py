#!/usr/bin/env python3
"""
Tests for pipeline.py - Interactive CLI Manager

Tests cover:
- Version discovery and status checking
- Version creation from template
- Version switching
- Version validation
- Build artifact cleaning
- Version duplication and deletion
- Helper functions
"""

import sys
from pathlib import Path
import pytest
import shutil

# Add parent directory to path to import pipeline module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import pipeline


class TestVersionDiscovery:
    """Tests for version discovery and status functions."""

    def test_get_available_versions_empty(self, tmp_path):
        """Test getting versions from empty directory."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        # Change to test directory
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            versions = pipeline.get_available_versions()
            assert versions == []
        finally:
            os.chdir(original_cwd)

    def test_get_available_versions_with_versions(self, tmp_path):
        """Test getting versions from directory with versions."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        # Create test versions
        (content_dir / 'version1').mkdir()
        (content_dir / 'version2').mkdir()
        (content_dir / '_template').mkdir()  # Should be excluded
        (content_dir / '_other').mkdir()  # Should be excluded

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            versions = pipeline.get_available_versions()
            assert versions == ['version1', 'version2']
        finally:
            os.chdir(original_cwd)

    def test_get_version_status_not_found(self, tmp_path):
        """Test status for non-existent version."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            status = pipeline.get_version_status('nonexistent')
            assert status == '[Not Found]'
        finally:
            os.chdir(original_cwd)

    def test_get_version_status_empty(self, tmp_path):
        """Test status for empty version directory."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            status = pipeline.get_version_status('test_version')
            assert status == '[Empty]'
        finally:
            os.chdir(original_cwd)

    def test_get_version_status_partial(self, tmp_path):
        """Test status for partially complete version."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        # Create only tagline
        (version_dir / 'tagline.tex').write_text('Test tagline')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            status = pipeline.get_version_status('test_version')
            assert status == '[Partial]'
        finally:
            os.chdir(original_cwd)

    def test_get_version_status_resume_ready(self, tmp_path):
        """Test status for resume-ready version (no cover letter)."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        # Create tagline and experience
        (version_dir / 'tagline.tex').write_text('Test tagline')
        (version_dir / 'experience.tex').write_text('Test experience')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            status = pipeline.get_version_status('test_version')
            assert status == '[Resume Ready]'
        finally:
            os.chdir(original_cwd)

    def test_get_version_status_complete(self, tmp_path):
        """Test status for complete version."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        # Create all required files
        (version_dir / 'tagline.tex').write_text('Test tagline')
        (version_dir / 'experience.tex').write_text('Test experience')
        (version_dir / 'cover_letter.tex').write_text('Test cover letter')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            status = pipeline.get_version_status('test_version')
            assert status == '[Complete]'
        finally:
            os.chdir(original_cwd)


class TestVersionManagement:
    """Tests for version creation and management."""

    def test_get_current_version_no_file(self, tmp_path):
        """Test getting current version when cv-version.tex doesn't exist."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            version = pipeline.get_current_version()
            assert version == 'default'
        finally:
            os.chdir(original_cwd)

    def test_get_current_version_with_file(self, tmp_path):
        """Test getting current version from cv-version.tex."""
        version_file = tmp_path / 'cv-version.tex'
        version_file.write_text(r'\newcommand{\OutputVersion}{test_version}')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            version = pipeline.get_current_version()
            assert version == 'test_version'
        finally:
            os.chdir(original_cwd)

    def test_update_version(self, tmp_path):
        """Test updating version in cv-version.tex."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            pipeline.update_version('new_version')

            version_file = tmp_path / 'cv-version.tex'
            assert version_file.exists()

            content = version_file.read_text()
            assert r'\newcommand{\OutputVersion}{new_version}' in content
        finally:
            os.chdir(original_cwd)


class TestValidation:
    """Tests for version validation functionality."""

    def test_validate_nonexistent_version(self, tmp_path):
        """Test validating non-existent version returns False."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('nonexistent')
            assert result is False
        finally:
            os.chdir(original_cwd)

    def test_validate_empty_version(self, tmp_path):
        """Test validating empty version (no .tex files)."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            assert result is True  # No files is not an error
        finally:
            os.chdir(original_cwd)

    def test_validate_clean_file(self, tmp_path):
        """Test validating clean LaTeX file."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        tex_file.write_text(r'\section{Test}' + '\n' + r'Clean content')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            assert result is True
        finally:
            os.chdir(original_cwd)

    def test_validate_control_characters(self, tmp_path):
        """Test validation detects control characters."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        # Add control character (ASCII 7 = bell)
        tex_file.write_text('Test\x07Content')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            assert result is False  # Should fail due to control character
        finally:
            os.chdir(original_cwd)

    def test_validate_template_placeholders(self, tmp_path):
        """Test validation warns about template placeholders."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        tex_file.write_text('[Your Name] [Job Title]')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            # Should pass with warnings
            assert result is True
        finally:
            os.chdir(original_cwd)

    def test_validate_begin_without_end(self, tmp_path):
        """Test validation warns about unclosed begin blocks."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        tex_file.write_text(r'\begin{document}' + '\n' + r'Content here' + '\n')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            # Should pass with warnings about missing \end{document}
            assert result is True
        finally:
            os.chdir(original_cwd)

    def test_validate_begin_with_end(self, tmp_path):
        """Test validation passes for properly closed environments."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        tex_file.write_text(
            r'\begin{document}' + '\n' +
            r'Content here' + '\n' +
            r'\end{document}' + '\n'
        )

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            # Should pass without warnings
            assert result is True
        finally:
            os.chdir(original_cwd)

    def test_validate_trailing_whitespace(self, tmp_path):
        """Test validation warns about trailing whitespace."""
        content_dir = tmp_path / '_content'
        version_dir = content_dir / 'test_version'
        version_dir.mkdir(parents=True)

        tex_file = version_dir / 'test.tex'
        tex_file.write_text('Line with trailing space   \nAnother line')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.validate_version('test_version')
            # Should pass with warnings
            assert result is True
        finally:
            os.chdir(original_cwd)


class TestCleanArtifacts:
    """Tests for build artifact cleaning."""

    def test_clean_no_artifacts(self, tmp_path):
        """Test cleaning when no artifacts exist."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.clean_build_artifacts()
            assert result is True
        finally:
            os.chdir(original_cwd)

    def test_clean_with_artifacts(self, tmp_path):
        """Test cleaning LaTeX artifacts."""
        # Create some artifacts
        (tmp_path / 'test.aux').write_text('aux content')
        (tmp_path / 'test.log').write_text('log content')
        (tmp_path / 'test.out').write_text('out content')

        pycache = tmp_path / '__pycache__'
        pycache.mkdir()
        (pycache / 'test.pyc').write_text('pyc content')

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.clean_build_artifacts()
            assert result is True

            # Check artifacts were removed
            assert not (tmp_path / 'test.aux').exists()
            assert not (tmp_path / 'test.log').exists()
            assert not (tmp_path / 'test.out').exists()
            assert not pycache.exists()
        finally:
            os.chdir(original_cwd)


class TestVersionDuplication:
    """Tests for version duplication."""

    def test_duplicate_nonexistent_source(self, tmp_path):
        """Test duplicating non-existent version."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.duplicate_version('nonexistent', 'new_version')
            assert result is False
        finally:
            os.chdir(original_cwd)

    def test_duplicate_to_existing_dest(self, tmp_path):
        """Test duplicating to existing destination."""
        content_dir = tmp_path / '_content'
        source_dir = content_dir / 'source'
        dest_dir = content_dir / 'dest'
        source_dir.mkdir(parents=True)
        dest_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.duplicate_version('source', 'dest')
            assert result is False
        finally:
            os.chdir(original_cwd)


class TestVersionDeletion:
    """Tests for version deletion."""

    def test_delete_nonexistent_version(self, tmp_path):
        """Test deleting non-existent version."""
        content_dir = tmp_path / '_content'
        content_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.delete_version('nonexistent')
            assert result is False
        finally:
            os.chdir(original_cwd)

    def test_delete_special_directory(self, tmp_path):
        """Test deleting special directory (starting with _)."""
        content_dir = tmp_path / '_content'
        special_dir = content_dir / '_template'
        special_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            result = pipeline.delete_version('_template')
            assert result is False
            assert special_dir.exists()  # Should not be deleted
        finally:
            os.chdir(original_cwd)


class TestColorFunctions:
    """Tests for color output functions."""

    def test_print_functions_dont_crash(self, capsys):
        """Test that print functions execute without errors."""
        pipeline.print_header("Test Header")
        pipeline.print_success("Success message")
        pipeline.print_error("Error message")
        pipeline.print_info("Info message")
        pipeline.print_warning("Warning message")

        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "Success message" in captured.out
        assert "Error message" in captured.out
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
