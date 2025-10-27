#!/usr/bin/env python3
"""Tests for cv_utils shared utilities."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_utils import (
    Colors,
    print_status,
    read_text_file,
    write_text_file,
    read_text_file_safe,
    file_exists,
    ensure_dir_exists,
    get_file_content_or_none,
)


class TestConsoleUtilities:
    """Test console output utilities."""

    def test_colors_attributes_exist(self):
        """Test that Colors class has all expected attributes."""
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'RESET')
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'DIM')

    def test_print_status_doesnt_crash(self):
        """Test that print_status function works without errors."""
        # Just verify these don't crash
        print_status("test message", "success")
        print_status("test message", "error")
        print_status("test message", "warning")
        print_status("test message", "info")


class TestFileIOUtilities:
    """Test file I/O utilities."""

    def test_read_write_text_file(self, tmp_path):
        """Test basic file reading and writing."""
        test_file = tmp_path / "test.txt"
        content = "Test content\nWith multiple lines"

        write_text_file(test_file, content)
        assert test_file.exists()

        read_content = read_text_file(test_file)
        assert read_content == content

    def test_read_text_file_safe_existing(self, tmp_path):
        """Test safe reading of existing file."""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        write_text_file(test_file, content)

        result = read_text_file_safe(test_file)
        assert result == content

    def test_read_text_file_safe_nonexistent(self, tmp_path):
        """Test safe reading of nonexistent file returns default."""
        test_file = tmp_path / "nonexistent.txt"

        result = read_text_file_safe(test_file)
        assert result == ""

        result_custom = read_text_file_safe(test_file, default="custom default")
        assert result_custom == "custom default"

    def test_file_exists(self, tmp_path):
        """Test file existence checking."""
        test_file = tmp_path / "test.txt"
        assert not file_exists(test_file)

        write_text_file(test_file, "content")
        assert file_exists(test_file)

    def test_ensure_dir_exists(self, tmp_path):
        """Test directory creation."""
        test_dir = tmp_path / "nested" / "directory" / "structure"
        assert not test_dir.exists()

        result = ensure_dir_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

        # Should not raise error if already exists
        result2 = ensure_dir_exists(test_dir)
        assert result2 == test_dir

    def test_get_file_content_or_none(self, tmp_path):
        """Test getting file content or None."""
        test_file = tmp_path / "test.txt"

        # Nonexistent file returns None
        result = get_file_content_or_none(test_file)
        assert result is None

        # Existing file returns content
        content = "Test content"
        write_text_file(test_file, content)
        result = get_file_content_or_none(test_file)
        assert result == content
