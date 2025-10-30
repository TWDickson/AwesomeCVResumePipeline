"""Project path utilities for CV scripts."""

from pathlib import Path
from typing import Optional


class ProjectPaths:
    """Centralized project path management."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize project paths.

        Args:
            base_dir: Project root directory. If None, auto-detect from script location.
        """
        if base_dir is None:
            # Auto-detect: go up from scripts/ to project root
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.base_dir = Path(base_dir).resolve()

    @property
    def content_dir(self) -> Path:
        """Path to _content/ directory."""
        return self.base_dir / "_content"

    @property
    def template_dir(self) -> Path:
        """Path to _content/_template/ directory."""
        return self.content_dir / "_template"

    @property
    def cv_library_dir(self) -> Path:
        """Path to cv_library/ directory."""
        return self.base_dir / "cv_library"

    @property
    def output_dir(self) -> Path:
        """Path to _output/ directory."""
        return self.base_dir / "_output"

    @property
    def scripts_dir(self) -> Path:
        """Path to scripts/ directory."""
        return self.base_dir / "scripts"

    @property
    def vscode_dir(self) -> Path:
        """Path to .vscode/ directory."""
        return self.base_dir / ".vscode"

    @property
    def personal_details_file(self) -> Path:
        """Path to cv-personal-details.tex file."""
        return self.base_dir / "cv-personal-details.tex"

    @property
    def version_file(self) -> Path:
        """Path to cv-version.tex file."""
        return self.base_dir / "cv-version.tex"

    def version_dir(self, version: str) -> Path:
        """
        Get path to a specific version directory.

        Args:
            version: Version name

        Returns:
            Path to _content/{version}/ directory
        """
        return self.content_dir / version

    def output_version_dir(self, version: str) -> Path:
        """
        Get path to a specific version output directory.

        Args:
            version: Version name

        Returns:
            Path to _output/{version}/ directory
        """
        return self.output_dir / version


def get_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find project root by looking for characteristic files.

    Args:
        start_path: Starting path for search. If None, use current file location.

    Returns:
        Project root path
    """
    if start_path is None:
        start_path = Path(__file__).resolve()

    # Look for project markers
    markers = ['cv-resume.tex', 'cv-version.tex', '_content', 'cv_library']

    current = start_path if start_path.is_dir() else start_path.parent

    # Walk up directory tree
    for _ in range(10):  # Limit depth to prevent infinite loops
        # Check if any marker exists
        if any((current / marker).exists() for marker in markers):
            return current

        # Go up one level
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    # Fallback: assume we're in scripts/ and go up two levels
    return Path(__file__).resolve().parent.parent
