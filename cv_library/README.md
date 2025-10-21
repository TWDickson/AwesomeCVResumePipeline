# CV Library

## experience_library.json

Array of jobs merged by company+dates.

```json
[{
  "titles": ["Role Variant 1", "Role Variant 2"],
  "company": "Employer Name",
  "location": "City, Country",
  "dates": "YYYY - YYYY",
  "achievements": ["Bullet 1", "Bullet 2"]
}]
```

## skills_library.json

Skills by job application context. Keys show which role the skills were chosen for.

```json
{
  "cv_directory_name": {
    "Category Name": ["Skill 1", "Skill 2"]
  }
}
```

Regenerate: `python3 cv_parser.py`
