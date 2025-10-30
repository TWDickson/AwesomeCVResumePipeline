#!/usr/bin/env python3
"""
VS Code Tasks Generator
Generates tasks.json with dynamic version list from _content/ directory.

Usage:
    python generate_tasks.py
"""

import json
import sys
from pathlib import Path
from typing import List

# Add scripts directory to path for cv_utils import
sys.path.insert(0, str(Path(__file__).parent))
from cv_utils import ProjectPaths, print_status, ensure_dir_exists, require_directory  # noqa: E402


def get_available_versions(content_path: Path) -> List[str]:
    """Get sorted list of version names from _content/ directory."""
    versions = sorted([
        d.name for d in content_path.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ])
    return versions


def generate_tasks_json(versions: List[str]) -> dict:
    """Generate tasks.json structure with dynamic version list."""
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Set CV Version",
                "type": "shell",
                "command": "python",
                "args": [
                    "${workspaceFolder}/scripts/set_version.py",
                    "${input:cvVersion}"
                ],
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "List CV Versions",
                "type": "shell",
                "command": "python",
                "args": [
                    "${workspaceFolder}/scripts/set_version.py",
                    "--list"
                ],
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Parse CV to JSON Library",
                "type": "shell",
                "command": "python",
                "args": [
                    "${workspaceFolder}/scripts/cv_parser.py"
                ],
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Update Tasks (Refresh Version List)",
                "type": "shell",
                "command": "python",
                "args": [
                    "${workspaceFolder}/scripts/generate_tasks.py"
                ],
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            }
        ],
        "inputs": [
            {
                "id": "cvVersion",
                "type": "pickString",
                "description": "Select CV version",
                "options": versions if versions else ["default"],
                "default": versions[0] if versions else "default"
            }
        ]
    }


def main() -> None:
    """Main entry point."""
    # Initialize project paths
    paths = ProjectPaths()

    # Ensure _content directory exists
    require_directory(
        paths.content_dir,
        f"_content/ directory not found at {paths.content_dir}"
    )

    # Create .vscode directory if it doesn't exist
    ensure_dir_exists(paths.vscode_dir)

    # Get available versions
    versions = get_available_versions(paths.content_dir)

    # Generate tasks.json (handles empty list gracefully)
    tasks_data = generate_tasks_json(versions)

    # Write to file
    tasks_file = paths.vscode_dir / "tasks.json"
    try:
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=4, ensure_ascii=False)

        print_status(f"Generated {tasks_file}", 'success')
        if versions:
            print(f"  Found {len(versions)} version(s): {', '.join(versions)}")
        else:
            print("  No versions found - using 'default' as placeholder")
    except Exception as e:
        print_status(f"Error writing tasks.json: {e}", 'error')
        sys.exit(1)


if __name__ == '__main__':
    main()
