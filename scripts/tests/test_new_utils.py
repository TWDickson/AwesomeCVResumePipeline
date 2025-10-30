#!/usr/bin/env python3
"""Tests for new cv_utils modules: project_paths, version_utils, error_handling."""

import sys
import pytest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_utils import (  # noqa: E402
    ProjectPaths,
    get_project_root,
    get_current_version,
    get_version_status,
    set_version,
    extract_name_from_personal_details,
    CVScriptError,
    handle_error,
    require_file,
    require_directory,
    warn,
    Colors,
)


class TestProjectPaths:
    """Test ProjectPaths class for centralized path management."""

    def test_project_paths_initialization(self, tmp_path):
        """Test ProjectPaths can be initialized with a base directory."""
        paths = ProjectPaths(tmp_path)
        assert paths.base_dir == tmp_path.resolve()

    def test_project_paths_auto_detection(self):
        """Test ProjectPaths can auto-detect project root."""
        paths = ProjectPaths()
        assert paths.base_dir.exists()
        assert paths.base_dir.is_dir()

    def test_content_dir_property(self, tmp_path):
        """Test content_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "_content"
        assert paths.content_dir == expected

    def test_template_dir_property(self, tmp_path):
        """Test template_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "_content" / "_template"
        assert paths.template_dir == expected

    def test_cv_library_dir_property(self, tmp_path):
        """Test cv_library_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "cv_library"
        assert paths.cv_library_dir == expected

    def test_output_dir_property(self, tmp_path):
        """Test output_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "_output"
        assert paths.output_dir == expected

    def test_scripts_dir_property(self, tmp_path):
        """Test scripts_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "scripts"
        assert paths.scripts_dir == expected

    def test_vscode_dir_property(self, tmp_path):
        """Test vscode_dir property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / ".vscode"
        assert paths.vscode_dir == expected

    def test_personal_details_file_property(self, tmp_path):
        """Test personal_details_file property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "cv-personal-details.tex"
        assert paths.personal_details_file == expected

    def test_version_file_property(self, tmp_path):
        """Test version_file property returns correct path."""
        paths = ProjectPaths(tmp_path)
        expected = tmp_path / "cv-version.tex"
        assert paths.version_file == expected

    def test_version_dir_method(self, tmp_path):
        """Test version_dir method returns correct path for a version."""
        paths = ProjectPaths(tmp_path)
        version = "test_version"
        expected = tmp_path / "_content" / version
        assert paths.version_dir(version) == expected

    def test_output_version_dir_method(self, tmp_path):
        """Test output_version_dir method returns correct path."""
        paths = ProjectPaths(tmp_path)
        version = "test_version"
        expected = tmp_path / "_output" / version
        assert paths.output_version_dir(version) == expected


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_get_project_root_with_markers(self, tmp_path):
        """Test get_project_root finds root with marker files."""
        # Create marker file
        marker = tmp_path / "cv-resume.tex"
        marker.touch()

        # Create subdirectory to search from
        subdir = tmp_path / "scripts" / "tests"
        subdir.mkdir(parents=True)

        root = get_project_root(subdir)
        assert root == tmp_path

    def test_get_project_root_with_content_dir(self, tmp_path):
        """Test get_project_root finds root with _content directory."""
        content_dir = tmp_path / "_content"
        content_dir.mkdir()

        subdir = tmp_path / "scripts"
        subdir.mkdir()

        root = get_project_root(subdir)
        assert root == tmp_path

    def test_get_project_root_fallback(self, tmp_path):
        """Test get_project_root has reasonable fallback."""
        # Create a deep directory without markers
        deep_dir = tmp_path / "a" / "b" / "c" / "d"
        deep_dir.mkdir(parents=True)

        root = get_project_root(deep_dir)
        # Should return something reasonable, not crash
        assert root.exists()


class TestVersionUtils:
    """Test version utility functions."""

    def test_get_current_version_valid(self, tmp_path):
        """Test get_current_version with valid version file."""
        version_file = tmp_path / "cv-version.tex"
        version_file.write_text(
            r"""%-------------------------------------------------------------------------------
% Version Configuration
%-------------------------------------------------------------------------------

\newcommand{\OutputVersion}{test_version}
""",
            encoding='utf-8'
        )

        version = get_current_version(version_file)
        assert version == "test_version"

    def test_get_current_version_nonexistent(self, tmp_path):
        """Test get_current_version with nonexistent file."""
        version_file = tmp_path / "cv-version.tex"
        version = get_current_version(version_file)
        assert version is None

    def test_get_current_version_invalid_format(self, tmp_path):
        """Test get_current_version with invalid format."""
        version_file = tmp_path / "cv-version.tex"
        version_file.write_text("Invalid content", encoding='utf-8')

        version = get_current_version(version_file)
        assert version is None

    def test_get_version_status_complete(self, tmp_path):
        """Test get_version_status with complete version."""
        version_dir = tmp_path / "test_version"
        version_dir.mkdir()

        (version_dir / "tagline.tex").touch()
        (version_dir / "experience.tex").touch()
        (version_dir / "cover_letter.tex").touch()

        status, color = get_version_status(version_dir)
        assert status == " [Complete]"
        assert color == Colors.GREEN

    def test_get_version_status_resume_ready(self, tmp_path):
        """Test get_version_status with resume-ready version."""
        version_dir = tmp_path / "test_version"
        version_dir.mkdir()

        (version_dir / "tagline.tex").touch()
        (version_dir / "experience.tex").touch()

        status, color = get_version_status(version_dir)
        assert status == " [Resume Ready]"
        assert color == Colors.CYAN

    def test_get_version_status_partial(self, tmp_path):
        """Test get_version_status with partial version."""
        version_dir = tmp_path / "test_version"
        version_dir.mkdir()

        (version_dir / "tagline.tex").touch()

        status, color = get_version_status(version_dir)
        assert status == " [Partial]"
        assert color == Colors.YELLOW

    def test_get_version_status_empty(self, tmp_path):
        """Test get_version_status with empty version directory."""
        version_dir = tmp_path / "test_version"
        version_dir.mkdir()

        status, color = get_version_status(version_dir)
        assert status == ""
        assert color == Colors.RESET

    def test_set_version(self, tmp_path):
        """Test set_version writes correct content."""
        version_file = tmp_path / "cv-version.tex"
        version_name = "my_test_version"

        set_version(version_name, version_file)

        assert version_file.exists()
        content = version_file.read_text(encoding='utf-8')
        assert r"\newcommand{\OutputVersion}{my_test_version}" in content
        assert "Version Configuration" in content

    def test_set_version_overwrites(self, tmp_path):
        """Test set_version overwrites existing file."""
        version_file = tmp_path / "cv-version.tex"
        version_file.write_text("Old content", encoding='utf-8')

        set_version("new_version", version_file)

        content = version_file.read_text(encoding='utf-8')
        assert "Old content" not in content
        assert r"\newcommand{\OutputVersion}{new_version}" in content

    def test_extract_name_valid(self, tmp_path):
        """Test extract_name_from_personal_details with valid file."""
        personal_file = tmp_path / "cv-personal-details.tex"
        personal_file.write_text(
            r"""\name{John}{Doe}
\position{Software Engineer}
""",
            encoding='utf-8'
        )

        name = extract_name_from_personal_details(personal_file)
        assert name == "John Doe"

    def test_extract_name_with_spaces(self, tmp_path):
        """Test extract_name_from_personal_details handles extra spaces."""
        personal_file = tmp_path / "cv-personal-details.tex"
        personal_file.write_text(
            r"\name{  Jane  }{  Smith  }",
            encoding='utf-8'
        )

        name = extract_name_from_personal_details(personal_file)
        assert name == "Jane Smith"

    def test_extract_name_fallback(self, tmp_path):
        """Test extract_name_from_personal_details fallback."""
        personal_file = tmp_path / "cv-personal-details.tex"
        personal_file.write_text("No name here", encoding='utf-8')

        name = extract_name_from_personal_details(personal_file)
        assert name == "CV"

    def test_extract_name_nonexistent_file(self, tmp_path):
        """Test extract_name_from_personal_details with nonexistent file."""
        personal_file = tmp_path / "nonexistent.tex"

        name = extract_name_from_personal_details(personal_file)
        assert name == "CV"


class TestErrorHandling:
    """Test error handling utilities."""

    def test_cvscript_error_is_exception(self):
        """Test CVScriptError is an Exception."""
        error = CVScriptError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_handle_error_exits(self, capsys):
        """Test handle_error exits with correct code."""
        with pytest.raises(SystemExit) as exc_info:
            handle_error("Test error message", exit_code=42)

        assert exc_info.value.code == 42

        # Check error message was printed
        captured = capsys.readouterr()
        assert "Test error message" in captured.out

    def test_handle_error_default_exit_code(self):
        """Test handle_error uses default exit code of 1."""
        with pytest.raises(SystemExit) as exc_info:
            handle_error("Test error")

        assert exc_info.value.code == 1

    def test_require_file_exists(self, tmp_path):
        """Test require_file doesn't exit when file exists."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        # Should not raise
        require_file(test_file)

    def test_require_file_missing_default_message(self, tmp_path):
        """Test require_file exits with default message when file missing."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SystemExit):
            require_file(test_file)

    def test_require_file_missing_custom_message(self, tmp_path, capsys):
        """Test require_file exits with custom message."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(SystemExit):
            require_file(test_file, "Custom error message")

        captured = capsys.readouterr()
        assert "Custom error message" in captured.out

    def test_require_directory_exists(self, tmp_path):
        """Test require_directory doesn't exit when directory exists."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Should not raise
        require_directory(test_dir)

    def test_require_directory_missing(self, tmp_path):
        """Test require_directory exits when directory missing."""
        test_dir = tmp_path / "nonexistent_dir"

        with pytest.raises(SystemExit):
            require_directory(test_dir)

    def test_require_directory_is_file(self, tmp_path):
        """Test require_directory exits when path is a file."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(SystemExit):
            require_directory(test_file)

    def test_require_directory_custom_message(self, tmp_path, capsys):
        """Test require_directory exits with custom message."""
        test_dir = tmp_path / "nonexistent"

        with pytest.raises(SystemExit):
            require_directory(test_dir, "My custom directory error")

        captured = capsys.readouterr()
        assert "My custom directory error" in captured.out

    def test_warn_doesnt_exit(self, capsys):
        """Test warn prints warning but doesn't exit."""
        warn("This is a warning")

        captured = capsys.readouterr()
        assert "This is a warning" in captured.out

    def test_warn_with_color(self, capsys):
        """Test warn uses warning color."""
        warn("Warning message")

        captured = capsys.readouterr()
        # Should contain the warning message
        assert "Warning message" in captured.out


class TestIntegration:
    """Integration tests combining multiple utilities."""

    def test_project_paths_with_version_utils(self, tmp_path):
        """Test ProjectPaths works with version utilities."""
        paths = ProjectPaths(tmp_path)

        # Create version directory
        version_dir = paths.version_dir("test_version")
        version_dir.mkdir(parents=True)

        # Add some content
        (version_dir / "tagline.tex").touch()
        (version_dir / "experience.tex").touch()

        # Check status
        status, color = get_version_status(version_dir)
        assert status == " [Resume Ready]"

        # Set version
        set_version("test_version", paths.version_file)
        assert paths.version_file.exists()

        # Read version
        version = get_current_version(paths.version_file)
        assert version == "test_version"

    def test_full_workflow(self, tmp_path):
        """Test a complete workflow using all utilities."""
        paths = ProjectPaths(tmp_path)

        # Create project structure
        paths.content_dir.mkdir()
        paths.output_dir.mkdir()

        # Create a version
        version_name = "my_version"
        version_dir = paths.version_dir(version_name)
        version_dir.mkdir()

        # Add content files
        (version_dir / "tagline.tex").write_text("My Tagline", encoding='utf-8')
        (version_dir / "experience.tex").write_text("Experience", encoding='utf-8')
        (version_dir / "cover_letter.tex").write_text("Cover", encoding='utf-8')

        # Check it's complete
        status, color = get_version_status(version_dir)
        assert status == " [Complete]"
        assert color == Colors.GREEN

        # Set as current version
        set_version(version_name, paths.version_file)

        # Verify we can read it back
        current = get_current_version(paths.version_file)
        assert current == version_name

        # Create personal details
        personal_file = paths.personal_details_file
        personal_file.write_text(r"\name{Test}{User}", encoding='utf-8')

        # Extract name
        name = extract_name_from_personal_details(personal_file)
        assert name == "Test User"

        # Verify all paths are correct
        assert paths.version_dir(current) == version_dir
        assert paths.output_version_dir(current) == tmp_path / "_output" / version_name
