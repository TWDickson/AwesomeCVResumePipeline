# Test Fixtures for Resume Pipeline

This directory contains comprehensive test fixtures using SpongeBob SquarePants as a fictional test character. These fixtures are designed to thoroughly exercise all features of the resume pipeline system.

## Purpose

These test fixtures serve multiple purposes:

1. **Validation Testing**: Ensure the build system handles all template section types correctly
2. **Markdown Conversion Testing**: Verify LaTeX-to-Markdown conversion for all section formats
3. **CV Library Testing**: Test parsing and JSON export of all resume data types
4. **Example Templates**: Provide a comprehensive example of proper LaTeX formatting
5. **Safe Testing**: Allow testing without exposing real personal information

## Files

### Personal Information
- **cv-personal-details.tex**: Complete contact information using SpongeBob character details
  - Includes photo, name, position, address, phone, email, social media links
  - Tests all available personal detail fields

### Resume Sections
- **tagline.tex**: Professional headline for resume header
- **summary.tex**: Professional summary paragraph (cvparagraph format)
- **skills.tex**: Six skill categories with multiple items each (cvskills format)
- **experience.tex**: Five job positions spanning 1998-Present (cventries format)
  - Includes 4-8 bullet points per position
  - Tests date ranges, multiple employers, various job titles
- **education.tex**: Two educational entries (cventries format)
  - Certificate program and high school diploma
  - Tests education with and without bullet points
- **certificates.tex**: Five professional certifications (cvhonors format)
- **honors.tex**: Five awards spanning 1999-2024 (cvhonors format)
- **extracurricular.tex**: Three volunteer/community activities (cventries format)
- **writing.tex**: Three publications/writing projects (cventries format)
  - Book, newspaper column, research paper
- **presentation.tex**: Three speaking engagements (cventries format)
- **committees.tex**: Five committee/organization memberships (cvhonors format)

### Cover Letter
- **cover_letter.tex**: Comprehensive 6-paragraph cover letter
  - Uses `\storecontent{}` command for content storage
  - Professional format with proper structure
  - Tests special characters and LaTeX formatting

## Coverage

These fixtures provide comprehensive coverage of:

### Template Section Types
✅ cvparagraph (summary)
✅ cvskills (skills categories)
✅ cventries (experience, education, extracurricular, writing, presentations)
✅ cvhonors (certificates, honors, committees)

### LaTeX Features
✅ Multiple nested `\begin{cvitems}...\end{cvitems}` blocks
✅ Special characters (\&, \$, \%, etc.)
✅ Date ranges and formats
✅ Multi-line descriptions
✅ Subsections and grouping
✅ Storage commands (`\storecontent`)

### Data Complexity
✅ 5 different employers
✅ 25+ years of experience timeline
✅ 40+ total bullet points
✅ 6 skill categories with 30+ individual skills
✅ 15+ certifications, awards, and honors
✅ Multiple publication types
✅ Community involvement and volunteer work

## Using Test Fixtures

### For Manual Testing

1. Create a test version in `_content/`:
   ```bash
   mkdir -p _content/spongebob_test
   cp scripts/tests/fixtures/*.tex _content/spongebob_test/
   ```

2. Set the version in `cv-version.tex`:
   ```tex
   \newcommand{\OutputVersion}{spongebob_test}
   ```

3. Build the resume:
   ```bash
   python scripts/build.py --resume
   python scripts/build.py --coverletter
   ```

### For Automated Testing

```python
import shutil
from pathlib import Path

# Copy fixtures to test directory
fixtures_dir = Path("scripts/tests/fixtures")
test_content_dir = Path("_content/test_version")
test_content_dir.mkdir(parents=True, exist_ok=True)

for fixture in fixtures_dir.glob("*.tex"):
    shutil.copy(fixture, test_content_dir / fixture.name)
```

### For CV Library Testing

```bash
# Copy fixtures to a test version
mkdir -p _content/test_spongebob
cp scripts/tests/fixtures/*.tex _content/test_spongebob/

# Parse to JSON library
python scripts/cv_parser.py
```

### For Markdown Conversion Testing

```bash
# Build the resume with fixtures
python scripts/build.py --resume

# Check the generated markdown
cat "_output/spongebob_test/SpongeBob SquarePants Resume.md"
```

## Character Details

**Name**: SpongeBob SquarePants  
**Occupation**: Fry Cook at Krusty Krab (1999-Present)  
**Notable Achievements**:
- 374 consecutive Employee of the Month awards
- Over 1 million Krabby Patties prepared
- Certified Jellyfishing Professional
- Published author and keynote speaker

## Design Decisions

### Why SpongeBob?

1. **Universally Known**: Everyone recognizes the character, making reviews easy
2. **No Privacy Concerns**: Completely fictional, no real personal data at risk
3. **Rich Background**: 20+ years of lore provides realistic career history
4. **Appropriate Tone**: Maintains professionalism while being clearly test data
5. **Comprehensive**: Character has diverse activities (cooking, jellyfishing, karate) allowing realistic skill variety

### Realistic Content

Despite being fictional, the fixtures use:
- Proper professional resume language
- Realistic achievement metrics (percentages, numbers, timeframes)
- Authentic skill categories and technical terms
- Standard cover letter structure and tone
- Appropriate formatting and organization

This ensures the test data exercises the same code paths as real resumes.

## Maintenance

When adding new features to the resume pipeline:

1. Update these fixtures to include examples of the new feature
2. Add comments documenting what the fixture tests
3. Ensure all template section types are represented
4. Maintain the 20+ year career timeline for date range testing

## Testing Checklist

Use these fixtures to verify:

- [ ] All 11 template section types parse correctly
- [ ] LaTeX special characters convert properly
- [ ] Date ranges format consistently
- [ ] Nested cvitems blocks don't break parsing
- [ ] Markdown output includes all content (no truncation)
- [ ] CV library JSON exports successfully
- [ ] Cover letter builds and converts correctly
- [ ] Personal details extract properly
- [ ] Skills with ampersands (\&) handle correctly
- [ ] Long bullet lists don't cause issues
- [ ] Multiple employers and date ranges work
- [ ] All cvhonors variations parse correctly

## License

These test fixtures are part of the Resume Pipeline project and use fictional character data from SpongeBob SquarePants (©Nickelodeon/Viacom) for educational and testing purposes only.
