# CV Pipeline Scripts

This directory contains Python scripts for managing CV versions and building resumes/cover letters.

## Overview

All scripts are written in **Python 3.7+** for true cross-platform compatibility. They dynamically scan the `_content/` directory to find available CV versions and provide tools to switch between them.

Each version can have its own:

- `tagline.tex` - Custom tagline
- `experience.tex` - Customized experience section
- `skills.tex` - Tailored skills
- `summary.tex` - Version-specific summary
- `cover_letter.tex` - Custom cover letter

## Requirements

- Python 3.7 or higher
- **Tectonic** - Modern TeX engine for building PDFs (recommended)
  - macOS: `brew install tectonic`
  - Windows: Download prebuilt binary from [GitHub Releases](https://github.com/tectonic-typesetting/tectonic/releases)
  - Linux: See [Tectonic installation](https://tectonic-typesetting.github.io/install.html)
- No Python dependencies (uses standard library only)

## Project Structure

```
scripts/
├── cv_utils/                  # Shared utility modules
│   ├── __init__.py            # Package exports
│   ├── project_paths.py       # Centralized path management
│   ├── version_utils.py       # Version handling utilities
│   ├── error_handling.py      # Standardized error handling
│   ├── console.py             # Console output utilities
│   ├── file_io.py             # File I/O operations
│   ├── regex_parsing.py       # LaTeX text parsing
│   ├── section_extractors.py # Section extraction logic
│   ├── data_conversion.py     # Data format conversions
│   └── logging_utils.py       # Logging functionality
├── set_version.py             # Version management
├── generate_tasks.py          # VS Code tasks generator
├── build.py                   # Build system
├── copy_and_convert.py        # Post-build processor
├── cv_parser.py               # CV to JSON converter
├── latex_packages.py          # LaTeX package manager
└── tests/                     # Test suite
```

## Shared Utilities (`cv_utils/`)

The `cv_utils` package provides shared functionality used across all scripts:

### Core Modules

**`project_paths.py`** - Centralized path management
- `ProjectPaths` class for accessing all project directories
- Auto-detection of project root
- Single source of truth for project structure

**`version_utils.py`** - CV version management
- `get_current_version()` - Read version from cv-version.tex
- `get_version_status()` - Check version completeness
- `set_version()` - Write version to cv-version.tex
- `extract_name_from_personal_details()` - Parse user name from LaTeX

**`error_handling.py`** - Standardized error handling
- Custom exception classes for CV scripts
- `handle_error()` - Print error and exit gracefully
- `require_file()` / `require_directory()` - Validation helpers
- `warn()` - Print warnings without exiting

**`console.py`** - Console output formatting
- `Colors` class for ANSI color codes
- `print_status()` - Colored status messages (success, error, warning, info)

**`file_io.py`** - File operations
- Safe file reading/writing with UTF-8 encoding
- Path existence checking
- Directory creation helpers

## Scripts

### Core Scripts

1. **`build.py`** - Build resume and cover letter
   - Cross-platform PDF builder using Tectonic
   - Validates version content exists
   - Clear error messages and build status
   - No complex TeX distribution required

2. **`set_version.py`** - Set or list CV versions
   - Scans `_content/` directory
   - Updates `cv-version.tex` with selected version
   - Shows version status: [Complete], [Resume Ready], or [Partial]

3. **`generate_tasks.py`** - Generate VS Code tasks.json
   - Creates tasks with dynamic version picker
   - Auto-updates when new versions are added

4. **`copy_and_convert.py`** - LaTeX post-build processor
   - Copies compiled PDF to `_output/<version>/` directory
   - Dynamically names files using your name from `cv-personal-details.tex`
   - Generates markdown versions automatically
   - Called by LaTeX during compilation (via `\ShellEscape`)

### Utility Scripts

1. **`cv_parser.py`** - Parse CV content to JSON library
2. **`resume_to_markdown.py`** - Convert LaTeX resume to Markdown
3. **`cover_letter_to_markdown.py`** - Convert LaTeX cover letter to Markdown

### Test Suite

The `tests/` subdirectory contains comprehensive pytest tests for all scripts.

See [tests/README.md](tests/README.md) for detailed test documentation.

## Usage

### Build Resume & Cover Letter

The easiest way to build your documents is with the new Tectonic-based builder:

```bash
# Build both resume and cover letter
python scripts/build.py

# Build resume only
python scripts/build.py --resume

# Build cover letter only
python scripts/build.py --cover-letter

# Check if Tectonic is installed
python scripts/build.py --check
```

**Benefits of using Tectonic:**

- No need for full TeX Live installation (saves ~5GB)
- Automatically downloads only required packages
- Consistent builds across all platforms
- Fast and deterministic
- Better error messages

**VS Code Integration:**

- Press `Cmd+Shift+B` (Mac) or `Ctrl+Shift+B` (Windows/Linux) to build
- Or use `Tasks: Run Task` → `Build Resume & Cover Letter`

### Set CV Version

```bash
# List available versions with status indicators
python scripts/set_version.py --list
python scripts/set_version.py -l

# Set a specific version
python scripts/set_version.py test_version
python scripts/set_version.py generic
```

### Regenerate VS Code Tasks

```bash
# Updates .vscode/tasks.json with current versions
python scripts/generate_tasks.py
```

### Manual PDF Copy (if needed)

```bash
# Copy resume PDF and generate markdown
python scripts/copy_and_convert.py resume cv-resume test_version

# Copy cover letter PDF and generate markdown
python scripts/copy_and_convert.py coverletter cv-coverletter test_version
```

*Note: LaTeX automatically calls `copy_and_convert.py` during compilation, so manual execution is rarely needed.*

## VS Code Integration

The scripts automatically integrate with VS Code through tasks. After running `generate_tasks.py`, you can:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select from:
   - **Set CV Version** - Choose from a dropdown of available versions
   - **List CV Versions** - Display all versions with completion status
   - **Update Tasks** - Refresh the version list after adding new versions

## Version Status Indicators

When listing versions, you'll see status indicators:

- **[Complete]** (Green) - Has tagline, experience, AND cover letter
- **[Resume Ready]** (Cyan) - Has tagline and experience (no cover letter)
- **[Partial]** (Yellow) - Has some but not all required files

## How It Works

### LaTeX Compilation Flow

1. You compile `cv-resume.tex` or `cv-coverletter.tex`
2. LaTeX reads the version from `cv-version.tex`
3. LaTeX pulls content from `_content/<version>/` (or falls back to `default`)
4. After PDF generation, LaTeX calls `copy_and_convert.py` via `\ShellEscape`
5. The script:
   - Reads your name from `cv-personal-details.tex`
   - Copies PDF to `_output/<version>/` with proper naming
   - Generates markdown version automatically

### Dynamic Naming

PDFs are automatically named based on your personal details:

- Resume: `<Your Name> Resume.pdf`
- Cover Letter: `<Your Name> Cover Letter.pdf`

No hardcoded names - if you update `\name{First}{Last}` in `cv-personal-details.tex`, all outputs will use the new name.

## Creating New Versions

1. Create a new folder in `_content/` with your version name (e.g., `_content/my_company/`)
2. Copy files from `_content/_template/` as a starting point
3. Customize the files for your specific use case
4. Run `generate-tasks` to refresh the version list
5. Use `set-version` to switch to your new version

## Testing

The scripts include comprehensive pytest tests (35 tests total) to ensure reliability:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest scripts/tests/test_cv_parser.py -v
```

See [tests/README.md](tests/README.md) for complete test documentation.

## File Structure

```text
scripts/
├── README.md                      # This file
├── set_version.py                 # Version management
├── generate_tasks.py              # VS Code tasks generator
├── copy_and_convert.py            # PDF copy and markdown generation
├── cv_parser.py                   # CV to JSON library parser
├── resume_to_markdown.py          # Resume LaTeX to Markdown
├── cover_letter_to_markdown.py    # Cover letter LaTeX to Markdown
└── tests/                         # Test suite
    ├── README.md                  # Test documentation
    ├── test_cv_parser.py          # Tests for cv_parser
    └── test_resume_to_markdown.py # Tests for resume converter
```

## Notes

- The `_template` directory is always excluded from the version list
- Version names must match their folder names exactly
- The scripts update `cv-version.tex` in the pipeline root
- VS Code tasks are stored in `.vscode/tasks.json`
