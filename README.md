# Resume Pipeline

A LaTeX resume and cover letter pipeline for managing many job applications. Each application gets its own folder of `.tex` files, a single command builds the PDF, and structured JSON libraries of your experience let an LLM assistant tailor content to a job posting without inventing anything.

Built on a patched fork of [Awesome-CV](https://github.com/posquit0/Awesome-CV). The Python scripts use the standard library only.

## Features

- **One folder per application** under `_content/<version>/` (tagline, summary, skills, experience, cover letter).
- **One-command builds** with [Tectonic](https://tectonic-typesetting.github.io/), so no full TeX Live install is needed.
- **Version switching** through `cv-version.tex`, with fallback to a `default` version.
- **Output management:** PDFs are copied to `_output/<version>/` along with Markdown copies of the resume and cover letter.
- **CV library:** your base CV is parsed into JSON (`cv_library/`) so an LLM can mine real content.
- **LLM guidance** in `AGENTS.md`: section-by-section workflow, no fabrication, and AI writing patterns to avoid.
- **Interactive CLI** (`pipeline.py`) and generated VS Code tasks.

## Requirements

- Python 3.7+ (no pip packages needed)
- [Tectonic](https://tectonic-typesetting.github.io/en-US/install.html) (`brew install tectonic` on macOS)
- Git with submodule support

## Quick Start

```sh
git clone --recurse-submodules https://github.com/TWDickson/AwesomeCVResumePipeline.git
cd AwesomeCVResumePipeline
```

If you cloned without `--recurse-submodules`, run `git submodule update --init`.

1. **Add your details.** Edit `cv-personal-details.tex` (name, email, links).
2. **Create a version.** Run `python pipeline.py --new-version`, or copy `_content/_template/` to `_content/default/`, then fill in the files.
3. **Pick sections.** Edit `\loadSections{...}` in `cv-resume.tex`. List only sections you have files for.
4. **Build.**

   ```sh
   python pipeline.py --build
   ```

   The PDF is written to `_output/<version>/`.

The template includes optional section files (education, certificates, honors, committees, writing, presentation, extracurricular). Delete the ones you do not use and leave them commented out in `cv-resume.tex`.

## Common Commands

```sh
python pipeline.py                    # Interactive menu
python pipeline.py --build            # Build the active version
python pipeline.py --list             # List versions and completion status
python pipeline.py --set-version      # Switch the active version
python pipeline.py --new-version      # Create a version from the template
python pipeline.py --refresh-library  # Rebuild cv_library/*.json from your CV files
python pipeline.py --status           # Show pipeline status
python -m pytest                      # Run tests
```

Version status in `--list`:

| Status | Meaning |
|--------|---------|
| `[Complete]` | tagline, experience, and cover letter present |
| `[Resume Ready]` | tagline and experience present, no cover letter |
| `[Partial]` | required files missing |

## How It Works

1. `cv-resume.tex` or `cv-coverletter.tex` is compiled.
2. LaTeX reads the active version from `cv-version.tex`.
3. Content is loaded from `_content/<version>/`, falling back to `default`.
4. A post-build step copies the PDF to `_output/<version>/` and writes Markdown copies.

| File | Purpose |
|------|---------|
| `cv-version.tex` | Sets `\OutputVersion{<version>}`, the active `_content/` folder |
| `cv-resume.tex` | Resume entry point; `\loadSections` sets section order |
| `cv-coverletter.tex` | Cover letter entry point |
| `cv-personal-details.tex` | Name, contact info, links |
| `cv-config.tex` | Shared styling and theme |
| `resume-pipeline.cls` | Document class built on Awesome-CV |
| `cv_library/` | JSON content libraries (schemas in `cv_library/README.md`) |
| `scripts/` | Build, version, parsing, and conversion scripts |

## Using an LLM Assistant

Point your assistant at `AGENTS.md`. The intended loop:

1. Give it a job posting and your `cv_library/` content.
2. It drafts one section at a time, using only content from the library.
3. You review and approve each section before it writes the `.tex` files.

Run `python pipeline.py --refresh-library` after changing your base CV so the JSON stays current.

## Project Layout

```text
.
├── pipeline.py              # Interactive CLI and command entry point
├── cv-*.tex                 # Entry points, config, personal details, active version
├── resume-pipeline.cls      # LaTeX class
├── AwesomeCV/               # Git submodule (Awesome-CV fork)
├── _content/
│   └── _template/           # Copy this to start a version
├── _output/                 # Built PDFs and Markdown (git-ignored)
├── cv_library/              # JSON content libraries
└── scripts/                 # Python tooling and tests
```

In this repository `_content/` (except `_template/`) and `_output/` are git-ignored, so your real applications stay out of version control. If you keep your own copy private, change `.gitignore` to track them.

## Documentation

- [QUICK_SETUP.md](QUICK_SETUP.md): set up on a new machine
- [scripts/README.md](scripts/README.md): script reference
- [scripts/tests/README.md](scripts/tests/README.md): test suite
- [cv_library/README.md](cv_library/README.md): library schemas
- [AGENTS.md](AGENTS.md): LLM assistant instructions

## License

Source-available, non-commercial. See [LICENSE.md](LICENSE.md).
