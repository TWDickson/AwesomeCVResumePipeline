
# CV Library

Minimal JSON schema for each section, for LLM consumption. Regenerate with `python3 cv_parser.py`.

**File purposes:**

- **experience_library.json**: Work experience, merged by company and dates.
- **skills_library.json**: Skills grouped by job context and category.
- **education_library.json**: Education history (degrees, schools, dates).
- **certificates_library.json**: Professional certificates and issuers.
- **honors_library.json**: Honors and awards received.
- **committees_library.json**: Committee memberships and roles.
- **writing_library.json**: Writing projects, publications, or articles.
- **presentations_library.json**: Presentations, talks, or lectures.
- **extracurricular_library.json**: Extracurricular activities and organizations.

**Note:** If a section is not used, its JSON file will contain an empty array (`[]`) as a placeholder. The script will update these files automatically when content is available.

---

## experience_library.json

```json
[
  {
    "titles": ["Role Variant 1", "Role Variant 2"],
    "company": "Employer Name",
    "location": "City, Country",
    "dates": "YYYY - YYYY",
    "achievements": ["Bullet 1", "Bullet 2"]
  }
]
```

## skills_library.json

```json
{
  "cv_directory_name": {
    "Category Name": ["Skill 1", "Skill 2"]
  }
}
```

## education_library.json

```json
[
  {
    "title": "Degree Name",
    "organization": "University Name",
    "location": "City, Country",
    "dates": "YYYY - YYYY",
    "items": ["Detail 1", "Detail 2"]
  }
]
```

## certificates_library.json

```json
[
  {
    "name": "Certificate Name",
    "organization": "Issuer Name",
    "location": "City, Country",
    "date": "YYYY"
  }
]
```

## honors_library.json

```json
[
  {
    "name": "Honor or Award Name",
    "organization": "Issuer Name",
    "location": "City, Country",
    "date": "YYYY"
  }
]
```

## committees_library.json

```json
[
  {
    "name": "Committee Name",
    "organization": "Organization Name",
    "location": "City, Country",
    "date": "YYYY"
  }
]
```

## writing_library.json

```json
[
  {
    "title": "Writing Project Title",
    "organization": "Publisher/Org Name",
    "location": "City, Country",
    "dates": "YYYY - YYYY",
    "items": ["Detail 1", "Detail 2"]
  }
]
```

## presentations_library.json

```json
[
  {
    "title": "Presentation Title",
    "organization": "Event/Org Name",
    "location": "City, Country",
    "dates": "YYYY - YYYY",
    "items": ["Detail 1", "Detail 2"]
  }
]
```

## extracurricular_library.json

```json
[
  {
    "title": "Activity Name",
    "organization": "Org Name",
    "location": "City, Country",
    "dates": "YYYY - YYYY",
    "items": ["Detail 1", "Detail 2"]
  }
]
```
