# Resume Pipeline: Quick Setup

Set up the pipeline on a new computer.

## 1. Clone the Repository

```sh
git clone --recurse-submodules https://github.com/TWDickson/AwesomeCVResumePipeline.git
cd AwesomeCVResumePipeline
```

If you already cloned without submodules: `git submodule update --init`.

## 2. Install Python

Python 3.7 or newer. Get it from [python.org](https://www.python.org/downloads/) or use [pyenv](https://github.com/pyenv/pyenv).

## 3. Create a Virtual Environment (optional)

```sh
python3 -m venv .venv
source .venv/bin/activate
```

The scripts use only the standard library, so there is nothing to `pip install`. `requirements.txt` is documentation only.

## 4. Install Tectonic

[Tectonic](https://tectonic-typesetting.github.io/en-US/) is a self-contained LaTeX engine that downloads packages as needed.

```sh
brew install tectonic    # macOS
```

For other platforms, see the [install docs](https://tectonic-typesetting.github.io/en-US/install.html).

## 5. Add Your Details and Content

1. Edit `cv-personal-details.tex`.
2. Run `python pipeline.py --new-version` (or copy `_content/_template/` to `_content/default/`) and fill in the files.
3. Adjust `\loadSections{...}` in `cv-resume.tex` to match the sections you have.

## 6. Build

```sh
python pipeline.py --build
```

The PDF is written to `_output/<version>/`.

## 7. Optional

- Interactive menu: `python pipeline.py`
- VS Code tasks: open the folder in VS Code (`python pipeline.py --refresh-tasks` regenerates the version list).
- Run the tests: `python -m pytest`

## Keeping Your Applications Private

This repository git-ignores `_content/` (except `_template/`) and `_output/`. To track your own applications, keep a private copy of the repo and edit `.gitignore` there. A common setup is a private repo as `origin` and this public repo as a second remote:

```sh
git remote add public https://github.com/TWDickson/AwesomeCVResumePipeline.git
git fetch public
```

Pipeline changes can then be cherry-picked between the two. Review changed files for personal details before pushing anything to a public remote.

---

See `README.md` for an overview and `scripts/README.md` for script details.
