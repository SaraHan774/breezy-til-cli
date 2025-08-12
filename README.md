# 📝 TIL (Today I Learned) CLI

A simple and extensible command-line tool to help you capture, manage, and summarize your daily learning in markdown format.

## 🚀 Features

- 📌 Create TIL entries by category with customizable templates (`til note`)
- 🎨 Template system with built-in templates and custom template support (`til template`)
- 📊 Learning streak analysis with GitHub-style grass visualization (`til streak`)
- 🔗 Manage link lists with tags and titles (`til link`)
- 🔍 Full-text search (`til search`)
- 🧠 Fuzzy file lookup with `fzf` (`til find`)
- 📦 Generate zip summaries for review (`til zip`)
- ✅ Git commit/push support (`til save`)
- 🤖 **Auto Git management** - Schedule automatic daily commits (`til auto`)
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
pipx upgrade breezy-til-cli

# Or reinstall from source
pipx uninstall breezy-til-cli
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

### 📝 Note Management

```bash
# ✏️ til note [category] [--date YYYY-MM-DD] [--template TEMPLATE]
# Create or open a markdown file for today (or a specific date) in a given category.

til note android
til note kotlin --date 2025-07-20
til note python --template study
til note project --template project --date 2025-08-01
```

### 🎨 Template System

```bash
# 📋 til template list
# List all available templates

til template list

# 👁️ til template show --id TEMPLATE_ID
# Show the content of a specific template

til template show --id study

# ➕ til template create --id ID --name "Name" --description "Description" --file FILE
# Create a new custom template

til template create --id mytemplate --name "My Template" --description "Custom template" --file template.md

# 🗑️ til template delete --id TEMPLATE_ID
# Delete a custom template

til template delete --id mytemplate
```

### 📊 Streak Analysis

```bash
# 📈 til streak
# Show basic learning streak statistics

til streak

# 🌱 til streak --visual
# Show streak with GitHub-style grass visualization and weekly pattern

til streak --visual

# 🌿 til streak --grass-only
# Show only the grass visualization

til streak --grass-only

# 📊 til streak --weekly-only
# Show only the weekly pattern chart

til streak --weekly-only
```

### 🔗 Link Management

```bash
# 🔗 til link "url" [--title "text"] [--tag tagname] [--date YYYY-MM-DD]
# Add a checklist-style link to a monthly Links.md file.

til link "https://inflearn.com/kotlin" --title "Kotlin 강의" --tag kotlin
```

### 🔍 Search & Navigation

```bash
# 🔍 til search <keyword>
# Search for a keyword across all TIL files.

til search coroutine

# 🔎 til find
# Interactively browse TIL files using fzf.

til find
```

### 📦 Export & Summary

```bash
# 🗃️ til zip [--from YYYY-MM-DD --to YYYY-MM-DD]
# Create a monthly or custom-range TIL summary.

til zip                        # current month
til zip --from 2025-07-01 --to 2025-07-31
```

### 💾 Git Operations

```bash
# 💾 til save "commit message"
# Run git add . && git commit -m "..." && git push origin main

til save "💡 Add July TILs"

# 🤖 til auto [command] (자동 Git 관리)
# 정해진 시간에 자동으로 변경사항을 커밋/푸시

til auto setup --time 20:00                    # 매일 오후 8시에 자동 커밋 설정
til auto setup --time 20:00 --message "📝 Daily update"  # 커스텀 메시지와 함께
til auto status                               # 자동화 설정 상태 확인
til auto test                                 # 즉시 테스트 실행
til auto remove                               # 자동화 설정 제거
```

### 📚 Index Generation

```bash
# 📚 til index
# Regenerate the auto-indexed README.md file.

til index
```

## 🎨 Built-in Templates

The CLI comes with several built-in templates:

- **`default`**: General TIL template with learning objectives and key points
- **`project`**: Project review template with work progress and issues
- **`study`**: Structured learning template with concepts and exercises
- **`bugfix`**: Bug fixing template with debugging process and solutions
- **`minimal`**: Simple template with minimal sections

### Template Variables

Templates support the following variables:
- `{date}`: Current date (YYYY-MM-DD format)
- `{category}`: Category name

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
├── python/
│   └── 2025-08-01.md
├── .templates/
│   ├── templates.json
│   ├── default.md
│   ├── project.md
│   ├── study.md
│   ├── bugfix.md
│   └── minimal.md
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

3. **Use a specific template:**
   ```bash
   til note study --template study
   ```

4. **Check your learning streak:**
   ```bash
   til streak --visual
   ```

5. **Add a useful link:**
   ```bash
   til link "https://docs.python.org/3/" --title "Python Documentation" --tag python
   ```

6. **Search your TILs:**
   ```bash
   til search async
   ```

7. **Generate monthly summary:**
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

### If templates don't work:
```bash
# Check if template files exist
ls -la .templates/

# Reinstall to regenerate default templates
pip install . --force-reinstall
```

## 🎯 Advanced Usage

### 🤖 Auto Git Management

Set up automatic daily commits to maintain your learning streak:

1. **Setup automatic commits:**
   ```bash
   # 매일 오후 8시에 자동 커밋 설정
   til auto setup --time 20:00
   
   # 커스텀 메시지와 함께 설정
   til auto setup --time 20:00 --message "📝 Daily TIL update"
   ```

2. **Check status:**
   ```bash
   til auto status
   ```

3. **Test the automation:**
   ```bash
   til auto test
   ```

4. **Remove automation:**
   ```bash
   til auto remove
   ```

**Supported platforms:**
- **macOS**: Uses `launchd` (LaunchAgents)
- **Linux**: Uses `cron`
- **Windows**: Uses Task Scheduler

### Creating Custom Templates

1. Create a template file:
   ```markdown
   # TIL - {date} - {category}
   
   ## 🎯 Today's Goal
   - 
   
   ## 📚 What I Learned
   - 
   
   ## 💡 Key Insights
   - 
   ```

2. Create the template:
   ```bash
   til template create --id mytemplate --name "My Template" --description "Custom template" --file template.md
   ```

3. Use the template:
   ```bash
   til note mycategory --template mytemplate
   ```

### Analyzing Learning Patterns

Use the streak analysis to understand your learning habits:

```bash
# Basic statistics
til streak

# Visual analysis with grass chart
til streak --visual

# Only grass visualization
til streak --grass-only

# Only weekly pattern
til streak --weekly-only
```

## 🤝 Contributing

Feel free to contribute by:
- Adding new templates
- Improving streak analysis
- Enhancing search functionality
- Adding new features

## 📄 License

This project is licensed under the MIT License.
