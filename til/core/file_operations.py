import os
import re
from datetime import datetime
import subprocess

# Handle missing pathspec dependency gracefully
try:
    import pathspec
except ImportError:
    pathspec = None

def load_gitignore_patterns(base_dir: str):
    """Load .gitignore patterns."""
    if pathspec is None:
        # Return a dummy pathspec that matches nothing
        class DummyPathSpec:
            def match_file(self, path):
                return False
        return DummyPathSpec()
    
    gitignore_path = os.path.join(base_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    with open(gitignore_path, "r") as f:
        return pathspec.PathSpec.from_lines("gitwildmatch", f)

def ensure_category_folder(base_dir: str, category: str) -> str:
    """Ensure category folder exists."""
    folder = os.path.join(base_dir, category)
    os.makedirs(folder, exist_ok=True)
    return folder

def create_or_open_note(base_dir: str, category: str, date_str: str = None, editor: str = "code"):
    """Create or open a TIL note."""
    today = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    date = today.strftime("%Y-%m-%d")

    folder = ensure_category_folder(base_dir, category)
    filepath = os.path.join(folder, f"{date}.md")

    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write(f"# TIL - {date}\n\n- ")
        print(f"📄 Created new TIL entry: {filepath}")
    else:
        print(f"📂 Opening existing TIL entry: {filepath}")

    subprocess.run([editor, filepath])

def highlight_keyword(line: str, keyword: str) -> str:
    """Highlight keyword in a line."""
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f"\033[1;33m{m.group(0)}\033[0m", line)

def search_notes(base_dir: str, keyword: str):
    """Search for keyword in all TIL notes."""
    print(f"🔍 Searching for: \"{keyword}\" in TIL/")
    keyword_lower = keyword.lower()
    spec = load_gitignore_patterns(base_dir)

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)

            if spec.match_file(rel_path):
                continue

            try:
                with open(full_path, "r") as f:
                    for lineno, line in enumerate(f, start=1):
                        if keyword_lower in line.lower():
                            print(f"\n📄 {rel_path}:{lineno}")
                            print(f"    {highlight_keyword(line.strip(), keyword)}")
            except Exception as e:
                print(f"⚠️ Failed to read {rel_path}: {e}")

def interactive_find(base_dir: str, editor: str = "code"):
    """Interactive file finder using fzf."""
    print("🔍 Launching interactive file finder (fzf)...")

    spec = load_gitignore_patterns(base_dir)
    IGNORED_DIRS = {"venv", ".git", "__pycache__", ".mypy_cache"}

    # 전체 파일 목록 추출
    candidates = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            if not file.endswith(".md") or file == "README.md":
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            if spec.match_file(rel_path):
                continue
            candidates.append(rel_path)

    if not candidates:
        print("📭 No TIL files found.")
        return

    # fzf 실행
    try:
        result = subprocess.run(
            ["fzf"],
            input="\n".join(candidates),
            text=True,
            capture_output=True
        )
        selected = result.stdout.strip()
        if selected:
            target = os.path.join(base_dir, selected)
            print(f"📂 Opening: {target}")
            subprocess.run([editor, target])
        else:
            print("❌ Nothing selected.")
    except FileNotFoundError:
        print("❌ fzf is not installed. Try: brew install fzf")
