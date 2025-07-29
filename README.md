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

## 📦 Installation (recommended via pipx)

```bash
pipx install git+https://github.com/yourname/breezy-til-cli.git

or if working locally:

cd til/
pipx install .
```

## 📦 Update (recommended via pipx)

```bash
pipx reinstall git+https://github.com/yourname/breezy-til-cli.git
```

## Check Installed Version 

```bash 
pipx list
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
# Run git add . && git commit -m "...” && git push origin main

til save "💡 Add July TILs"


# 📚 til index
# Regenerate the auto-indexed README.md file.

til index

# ⚙️ Configuration (.tilrc)
# Create a .tilrc file in your TIL/ folder or home directory:

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

```
brew install fzf
```
