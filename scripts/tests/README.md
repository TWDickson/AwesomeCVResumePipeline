# Test Suite for Resume Pipeline Scripts

This directory contains comprehensive pytest tests for the resume generation and parsing scripts.

## Test Overview

**Total Tests:** 139 tests across 6 test files  
**Coverage:** Core utilities, parsers, converters, and refactored modules  
**Framework:** pytest with fixtures for isolated testing

## Test Files

### `test_new_utils.py` ⭐ NEW
Tests for refactored utility modules (`cv_utils/project_paths.py`, `cv_utils/version_utils.py`, `cv_utils/error_handling.py`):

**42 tests covering:**

- **ProjectPaths class** (12 tests):
  - Initialization with explicit and auto-detected base directory
  - All path properties (content_dir, template_dir, cv_library_dir, output_dir, etc.)
  - Version-specific path methods (version_dir, output_version_dir)
  
- **Project root detection** (3 tests):
  - Finding project root with marker files (cv-resume.tex, _content directory)
  - Fallback behavior for edge cases
  
- **Version utilities** (13 tests):
  - Reading current version from cv-version.tex (valid, invalid, missing)
  - Version status detection (Complete, Resume Ready, Partial, Empty)
  - Setting version with proper content generation
  - Name extraction from cv-personal-details.tex with fallback handling
  
- **Error handling** (12 tests):
  - CVScriptError exception class
  - handle_error() with custom exit codes
  - require_file() validation with custom messages
  - require_directory() validation including file-vs-directory checks
  - warn() function without exit
  
- **Integration tests** (2 tests):
  - Combined ProjectPaths + version utilities workflow
  - Full end-to-end workflow with all utilities

### `test_cv_utils.py`
Tests for shared utility functions:

- **Console utilities**: Color codes and status printing
- **File I/O**: Reading, writing, safe reading with defaults, existence checking, directory creation

### `test_resume.py`
Tests for the main interactive CLI manager (`pipeline.py`):

- **Version discovery**: Tests for finding and listing versions
- **Version status**: Tests status indicators (Complete, Resume Ready, Partial, Empty)
- **Version management**: Tests for getting/setting current version
- **Validation**: Tests for control character detection, LaTeX errors, template placeholders
- **Clean artifacts**: Tests for removing build artifacts and __pycache__
- **Duplication**: Tests for duplicating versions with validation
- **Deletion**: Tests for safe deletion with protection of special directories
- **Output functions**: Tests for colored terminal output

### `test_resume_to_markdown.py`
Tests for the LaTeX to Markdown converter (`resume_to_markdown.py`):

- **LaTeX text cleaning**: Tests for converting LaTeX formatting to Markdown
- **Personal info extraction**: Tests extraction from `cv-personal-details.tex`
- **Section parsers**:
  - `extract_summary()` - Summary text extraction
  - `extract_skills()` - Skills categories and items
  - `extract_experience()` - Job experience entries
  - `extract_cvhonors()` - Certificates, honors, committees
  - `extract_cventries_generic()` - Education, writing, presentations, extracurricular
- **Dynamic section ordering**: Tests reading section order from `cv-resume.tex`
- **Template filtering**: Ensures placeholder content is excluded

### `test_cv_parser.py`
Tests for the CV library builder (`cv_parser.py`):

- **Template hash loading**: Verifies template files are identified and skipped
- **All section parsers**:
  - Experience entries
  - Skills categories
  - Education
  - Certificates
  - Honors & Awards
  - Committees
  - Writing projects
  - Presentations
  - Extracurricular activities
- **Job merging**: Tests deduplication and merging of overlapping experiences
- **JSON export**: Validates output format and content
- **Text normalization**: Tests company name and date normalization

## Running Tests

### Run all tests from project root:
```bash
python -m pytest
```

### Run with verbose output:
```bash
python -m pytest -v
```

### Run specific test file:
```bash
python -m pytest scripts/tests/test_resume_to_markdown.py -v
```

### Run specific test class:
```bash
python -m pytest scripts/tests/test_cv_parser.py::TestCVParser -v
```

### Run specific test:
```bash
python -m pytest scripts/tests/test_resume_to_markdown.py::TestExtractCVHonors::test_simple_honor -v
```

## Test Coverage

All tests use the `tmp_path` pytest fixture to create isolated temporary directories, ensuring tests don't interfere with actual project files.

**Total Tests**: 60
**Coverage Areas**:
- Interactive CLI manager (25 tests)
  - Version discovery and status checking
  - Version creation, duplication, and deletion
  - Validation (8 comprehensive tests covering all code paths)
  - Artifact cleaning
  - Current version management
- LaTeX parsing and text cleaning (19 tests)
  - Personal information extraction
  - All 9+ resume section types
  - Template placeholder filtering
  - Dynamic section ordering
- CV library builder (16 tests)
  - Job merging and deduplication
  - JSON export functionality
  - Hash-based template detection

## Key Features Tested

### Template Filtering
Tests verify that placeholder content like `[Your Name]` and `[Job Title]` is automatically filtered out during parsing.

### Multiple Section Types
The test suite covers all resume section types:
- **cvparagraph**: Summary
- **cvskills**: Skills
- **cventries**: Experience, Education, Writing, Presentations, Extracurricular
- **cvhonors**: Certificates, Honors & Awards, Committees

### Dynamic Section Ordering
Tests confirm that the markdown generator respects the section order specified in `cv-resume.tex` via the `\loadSections{}` command.

### Subsection Support
Tests verify parsing of subsections (e.g., honors grouped by category) with proper hierarchical output.

## Configuration

Test configuration is defined in `/pytest.ini` at the project root.

## Requirements

- Python 3.7+
- pytest 8.0+
- No external dependencies beyond standard library

## Test Quality & Coverage Notes

### Lessons Learned

During development, we discovered a gap where validation tests passed but the actual function crashed at runtime. This happened because:

1. **Insufficient code path coverage**: The original tests didn't exercise all branches in the validation logic
2. **Missing edge case testing**: Tests used simple inputs that didn't trigger complex validation rules

### Improvements Made

To address this, we added comprehensive validation tests that exercise:
- **All regex patterns**: Tests now include `\begin{}` blocks to test environment validation
- **All warning types**: Trailing whitespace, template placeholders, mismatched braces
- **All error types**: Control characters, encoding errors, missing files
- **Both pass and fail scenarios**: Clean files, files with warnings, files with errors

### Best Practices

When adding new tests:

1. **Test all code paths**: Use `pytest --cov` (requires pytest-cov) to check coverage
2. **Test edge cases**: Include boundary conditions, empty inputs, malformed data
3. **Test both happy and sad paths**: Success cases AND failure cases
4. **Use realistic data**: Test with actual LaTeX constructs, not just simple strings
5. **Test error conditions**: Ensure errors are caught and handled gracefully

### Current Coverage

All major functions have comprehensive test coverage including:
- ✅ Version discovery and status checking (7 tests)
- ✅ Version management (create, update, get current) (3 tests)
- ✅ Validation with all code paths (8 tests)
- ✅ Artifact cleaning (2 tests)
- ✅ Version duplication (2 tests)
- ✅ Version deletion (2 tests)
- ✅ Output functions (1 test)

**Total: 60 tests covering all major functionality**
