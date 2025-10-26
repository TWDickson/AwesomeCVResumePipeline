# Taylor Dickson Resume Pipeline - Quick Setup Guide

This guide helps you set up the resume pipeline on a new computer (e.g., your work computer).

## 1. Clone the Repository

```sh
git clone https://github.com/TWDickson/Taylor-Dickson-Resume.git
cd Taylor-Dickson-Resume
```

## 2. Install Python
- Install Python 3.8 or newer (recommend using [python.org](https://www.python.org/downloads/) or [pyenv](https://github.com/pyenv/pyenv)).

## 3. Set Up a Virtual Environment
```sh
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install Python Dependencies
```sh
pip install -r requirements.txt
```

## 5. Install LaTeX (Tectonic recommended)
- [Tectonic](https://tectonic-typesetting.github.io/en-US/) is a modern LaTeX engine.
- Install via Homebrew (macOS):
  ```sh
  brew install tectonic
  ```
- Or see [Tectonic install docs](https://tectonic-typesetting.github.io/en-US/install.html) for other platforms.

## 6. Build Your Resume
```sh
python pipeline.py --build
```

## 7. (Optional) Use Interactive CLI
```sh
python pipeline.py
```

## 8. (Optional) VS Code Tasks
- Open the folder in VS Code for integrated build tasks.

---

For more details, see `scripts/README.md` or ask for help!
---

## 9. Public/Private Git Remote Setup

If you want to push to both a public and a private repository (e.g., GitHub and a work Git server):

1. **Clone your preferred remote (e.g., private):**
  ```sh
  git clone git@github.com:YourOrg/Taylor-Dickson-Resume.git
  cd Taylor-Dickson-Resume
  ```

2. **Add the other remote (e.g., public):**
  ```sh
  git remote add public git@github.com:TWDickson/Taylor-Dickson-Resume.git
  ```

3. **Check your remotes:**
  ```sh
  git remote -v
  ```

4. **Push to a specific remote:**
  ```sh
  git push public main
  git push origin main
  ```

5. **(Optional) Set up SSH keys for both accounts:**
  - Generate a new SSH key for work if needed.
  - Add the public key to your GitHub/work account.
  - Use an SSH config file (`~/.ssh/config`) to manage multiple keys:

    ```
    Host github.com-public
      HostName github.com
      User git
      IdentityFile ~/.ssh/id_rsa_public

    Host github.com-work
      HostName github.com
      User git
      IdentityFile ~/.ssh/id_rsa_work
    ```

  - Then use the correct host in your remote URL, e.g.:

    ```
    git remote set-url origin git@github.com-work:YourOrg/Taylor-Dickson-Resume.git
    git remote set-url public git@github.com-public:TWDickson/Taylor-Dickson-Resume.git
    ```
