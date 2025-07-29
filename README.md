# 📝 TIL (Today I Learned) CLI

A simple and extensible command-line tool to help you capture, manage, and summarize your daily learning in markdown format.

## 🚀 Features

- 📌 Create TIL entries by category (`til note`)
- 🔗 Manage link lists with tags and titles (`til link`)
- 🔍 Full-text search (`til search`)
- 🧠 Fuzzy file lookup with `fzf` (`til find`)
- 📦 Generate zip summaries for review (`til zip`)
- ✅ Git commit/push support (`til save`)
- 📚 Auto-generated README index (`til index`)
- ⚙️ Custom configuration via `.tilrc`

## 📦 Installation

### Using pipx (Recommended)

```bash
# Install from GitHub
pipx install git+https://github.com/trinity-uba/breezy-til-cli.git

# Or install from local directory
cd breezy-til-cli/
pipx install .
```

### Using pip (Alternative)

```bash
# Install from GitHub
pip install git+https://github.com/trinity-uba/breezy-til-cli.git

# Or install from local directory
cd breezy-til-cli/
pip install .
```

## 🔄 Updating

### Using pipx

```bash
# Update to latest version
pipx upgrade til

# Or reinstall from source
pipx uninstall til
pipx install git+https://github.com/trinity-uba/breezy-til-cli.git
```

### Using pip

```bash
# Update to latest version
pip install --upgrade breezy-til-cli
```

## 📋 Check Installed Version 

```bash 
# For pipx installations
pipx list

# For pip installations
pip show breezy-til-cli
```

## 🛠 Commands

```bash
# ✏️ til note [category] [--date YYYY-MM-DD]
# Create or open a markdown file for today (or a specific date) in a given category.

til note android
til note kotlin --date 2025-07-20

# 🔗 til link "url" [--title "text"] [--tag tagname] [--date YYYY-MM-DD]
# Add a checklist-style link to a monthly Links.md file.

til link "https://inflearn.com/kotlin" --title "Kotlin 강의" --tag kotlin

# 🔍 til search <keyword>
# Search for a keyword across all TIL files.

til search coroutine

# 🔎 til find
# Interactively browse TIL files using fzf.

til find

# 🗃️ til zip [--from YYYY-MM-DD --to YYYY-MM-DD]
# Create a monthly or custom-range TIL summary.

til zip                        # current month
til zip --from 2025-07-01 --to 2025-07-31

# 💾 til save "commit message"
# Run git add . && git commit -m "..." && git push origin main

til save "💡 Add July TILs"

# 📚 til index
# Regenerate the auto-indexed README.md file.

til index
```

## ⚙️ Configuration (.tilrc)

Create a `.tilrc` file in your TIL/ folder or home directory:

```ini
[general]
default_editor = code
default_category = uncategorized
default_link_tag = reference
open_browser = false
```

## 📁 Folder Structure Example

```
TIL/
├── android/
│   └── 2025-07-29.md
├── kotlin/
│   └── 2025-07-28.md
├── 2025/
│   └── 07/
│       └── 2025-07-01.md
├── 2025-07-Links.md
├── zip-2025-07.md
├── README.md
└── .tilrc
```

## 🧪 Requirements
- Python ≥ 3.8
- pipx (for global CLI install)
- fzf (optional, for til find)

### Install fzf (macOS):

```bash
brew install fzf
```

### Install fzf (Ubuntu/Debian):

```bash
sudo apt install fzf
```

## 🚀 Quick Start

1. **Install the CLI:**
   ```bash
   pipx install git+https://github.com/trinity-uba/breezy-til-cli.git
   ```

2. **Create your first TIL:**
   ```bash
   til note python
   ```

3. **Add a useful link:**
   ```bash
   til link "https://docs.python.org/3/" --title "Python Documentation" --tag python
   ```

4. **Search your TILs:**
   ```bash
   til search async
   ```

5. **Generate monthly summary:**
   ```bash
   til zip
   ```

## 🔧 Troubleshooting

### If you get "Package is not installed" error:
```bash
# Check what's actually installed
pipx list

# If you see 'til' is installed but with different name, uninstall and reinstall
pipx uninstall til
pipx install git+https://github.com/trinity-uba/breezy-til-cli.git
```

### If you get "'til' already seems to be installed" error:
```bash
# Force reinstall
pipx install --force git+https://github.com/trinity-uba/breezy-til-cli.git
```

### If you get import errors:
```bash
# Reinstall the package
pip uninstall breezy-til-cli -y
pip install .
```