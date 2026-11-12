# CLAUDE.md

Guidance for Claude Code when working in this repository. See `README.md` for the overview and `AGENTS.md` for the full resume-tailoring workflow.

## What This Project Is

A LaTeX resume and cover letter pipeline for many job applications. Each application is a folder under `_content/<version>/` with its own `.tex` files. Python scripts handle version switching, building, and the JSON content library in `cv_library/`.

## Common Commands

```bash
python pipeline.py                    # Interactive menu
python pipeline.py --build            # Build the active version to PDF
python pipeline.py --list             # List versions and status
python pipeline.py --set-version      # Switch the active version
python pipeline.py --new-version      # Create a version from _content/_template/
python pipeline.py --refresh-library  # Regenerate cv_library/*.json
python -m pytest                      # Run tests
```

Python 3.7+, standard library only. LaTeX compilation uses [Tectonic](https://tectonic-typesetting.github.io/).

## Architecture

- `cv-resume.tex` / `cv-coverletter.tex` are the entry points.
- `cv-version.tex` sets `\OutputVersion{<version>}`, which selects the `_content/` folder (falls back to `default`).
- `\loadSections{...}` in `cv-resume.tex` sets section order.
- Post-build, `scripts/copy_and_convert.py` copies the PDF to `_output/<version>/` and writes Markdown copies.
- Shared helpers live in `scripts/cv_utils/`.

## Working With Application Content

- Only use content from `cv_library/` or material the user provides. Never invent experience, skills, or roles.
- Work one section at a time: propose, get approval, then write the `.tex` file.
- Avoid AI writing patterns (see `AGENTS.md`): no em or en dashes, no trailing participials, no default groups of three, no inflated vocabulary.
- Prefer concrete actions, real numbers, and proper names over general claims.

## Public Repository Rules

Do not commit personal details, real application versions, personal `cv_library` content, or built output. `_content/` (except `_template/`) and `_output/` are git-ignored here. Keep `cv-personal-details.tex` as placeholders.
