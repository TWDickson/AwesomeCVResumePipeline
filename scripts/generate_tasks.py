#!/usr/bin/env python3
"""
VS Code Tasks Generator
Generates tasks.json with dynamic version list from _content/ directory.

Usage:
    python generate_tasks.py
"""

import json
from pathlib import Path
from typing import List


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
    # Get paths
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    content_path = base_dir / "_content"
    vscode_dir = base_dir / ".vscode"
    tasks_file = vscode_dir / "tasks.json"

    # Ensure _content directory exists
    if not content_path.exists():
        print(f"Error: _content/ directory not found at {content_path}")
        return

    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(exist_ok=True)

    # Get available versions
    versions = get_available_versions(content_path)

    # Generate tasks.json (handles empty list gracefully)
    tasks_data = generate_tasks_json(versions)

    # Write to file
    try:
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=4, ensure_ascii=False)

        print(f"✓ Generated {tasks_file}")
        if versions:
            print(f"  Found {len(versions)} version(s): {', '.join(versions)}")
        else:
            print("  No versions found - using 'default' as placeholder")
    except Exception as e:
        print(f"Error writing tasks.json: {e}")
        return


if __name__ == '__main__':
    main()
