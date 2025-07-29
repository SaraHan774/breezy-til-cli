#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import datetime
import argparse

# -------------------------------
# 0. 설정
# -------------------------------


SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

BASE_DIR = os.getcwd()
VENV_DIR = os.path.join(SCRIPT_DIR, "venv")
PYTHON_IN_VENV = os.path.join(VENV_DIR, "bin", "python3") if sys.platform != "win32" else os.path.join(VENV_DIR, "Scripts", "python.exe")
REQUIREMENTS = os.path.join(SCRIPT_DIR, "requirements.txt")
DEFAULT_TEMPLATE = "# TIL - {date}\n\n- "

# -------------------------------
# 1. 가상환경 자동 설정
# -------------------------------
def ensure_virtualenv():
    if sys.executable != PYTHON_IN_VENV:
        if not os.path.exists(VENV_DIR):
            print("⚙️  Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

        print("🔁 Re-running inside virtual environment...")
        subprocess.run([PYTHON_IN_VENV, __file__] + sys.argv[1:])
        sys.exit(0)

    # 가상환경 내에서만 실행되는 영역
    print(f"📂 Working in TIL base directory: {BASE_DIR}")

    # pathspec 없는 경우에만 설치
    try:
        import pathspec
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.run([PYTHON_IN_VENV, "-m", "pip", "install", "-r", REQUIREMENTS], check=True)

# -------------------------------
# 2. TIL 기능 구현 (main logic)
# -------------------------------

from configparser import ConfigParser

def load_tilrc_config():
    config = ConfigParser()

    # 우선순위: 현재 디렉토리 > 홈 디렉토리
    possible_paths = [
        os.path.join(BASE_DIR, ".tilrc"),
        os.path.expanduser("~/.tilrc")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            config.read(path)
            print(f"⚙️  Loaded settings from {path}")
            return config

    return config  # 빈 ConfigParser

CONFIG = load_tilrc_config()

DEFAULT_EDITOR = CONFIG.get("general", "default_editor", fallback="code")
DEFAULT_CATEGORY = CONFIG.get("general", "default_category", fallback=None)
DEFAULT_LINK_TAG = CONFIG.get("general", "default_link_tag", fallback=None)
OPEN_BROWSER = CONFIG.getboolean("general", "open_browser", fallback=False)

def load_gitignore_patterns(base_dir: str):
    import pathspec
    gitignore_path = os.path.join(base_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    with open(gitignore_path, "r") as f:
        return pathspec.PathSpec.from_lines("gitwildmatch", f)

def ensure_category_folder(category: str) -> str:
    folder = os.path.join(BASE_DIR, category)
    os.makedirs(folder, exist_ok=True)
    return folder

def create_or_open_note(category: str, date_str: str = None):
    today = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    date = today.strftime("%Y-%m-%d")

    folder = ensure_category_folder(category)
    filepath = os.path.join(folder, f"{date}.md")

    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write(f"# TIL - {date}\n\n- ")
        print(f"📄 Created new TIL entry: {filepath}")
    else:
        print(f"📂 Opening existing TIL entry: {filepath}")

    subprocess.run(["code", filepath])

def highlight_keyword(line: str, keyword: str) -> str:
    import re
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f"\033[1;33m{m.group(0)}\033[0m", line)

def search_notes(keyword: str):
    import pathspec
    print(f"🔍 Searching for: \"{keyword}\" in TIL/")
    keyword_lower = keyword.lower()
    spec = load_gitignore_patterns(BASE_DIR)

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BASE_DIR)

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

def render_entries(category: str, entries: list[tuple[str, str]]) -> list[str]:
    lines = []
    if len(entries) > 10:
        lines.append(f"\n<details>\n<summary>📁 {category} ({len(entries)} entries)</summary>\n")
        lines.append("")  # 줄바꿈

        for filename, rel_path in sorted(entries):
            date = filename.replace(".md", "")
            lines.append(f"- [{date}]({rel_path})")

        lines.append("\n</details>")
    else:
        lines.append(f"\n## 📁 {category}")
        for filename, rel_path in sorted(entries):
            date = filename.replace(".md", "")
            lines.append(f"- [{date}]({rel_path})")
    return lines

def update_index():
    import pathspec

    print("🛠  Updating TIL/README.md ...")

    index_lines = [
        "# 📝 TIL Index",
        "",
        "This is an automatically generated index of all your TIL files.",
        "",
        "## 🛠 Features (powered by `til.py`)",
        "",
        "- `til note [category] [--date YYYY-MM-DD]` → 주제별 TIL 생성",
        "- `til link \"url\" [--title] [--tag] [--date]` → 링크 관리 + Links.md 생성",
        "- `til search <keyword>` → 전체 TIL 텍스트 검색",
        "- `til find` → fzf 기반 빠른 파일 탐색",
        "- `til zip` → 이번 달 TIL 압축 / `--from --to` 지정 가능",
        "- `til save \"commit msg\"` → git add + commit + push 자동",
        "- `til index` → 이 인덱스 파일을 생성합니다 😄",
        "",
        "---"
    ]
    categorized = {}
    uncategorized = []

    # .gitignore 지원
    def load_gitignore_patterns(base_dir: str):
        gitignore_path = os.path.join(base_dir, ".gitignore")
        if not os.path.exists(gitignore_path):
            return pathspec.PathSpec.from_lines("gitwildmatch", [])
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)

    spec = load_gitignore_patterns(BASE_DIR)

    # 무시할 디렉토리 명시
    IGNORED_DIRS = {"venv", "__pycache__", ".pytest_cache", ".git", ".idea", ".mypy_cache", ".DS_Store"}

    # 마크다운 블록 렌더링
    def render_entries(category: str, entries: list[tuple[str, str]]) -> list[str]:
        lines = []
        if len(entries) > 10:
            lines.append(f"\n<details>\n<summary>📁 {category} ({len(entries)} entries)</summary>\n")
            lines.append("")
            for filename, rel_path in sorted(entries):
                date = filename.replace(".md", "")
                lines.append(f"- [{date}]({rel_path})")
            lines.append("\n</details>")
        else:
            lines.append(f"\n## 📁 {category}")
            for filename, rel_path in sorted(entries):
                date = filename.replace(".md", "")
                lines.append(f"- [{date}]({rel_path})")
        return lines

    # 파일 탐색
    for root, dirs, files in os.walk(BASE_DIR):
        # 무시할 디렉토리 제외
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in sorted(files):
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BASE_DIR)

            if spec.match_file(rel_path):
                continue

            path_parts = rel_path.split(os.sep)
            if len(path_parts) == 2:
                category, filename = path_parts
                categorized.setdefault(category, []).append((filename, rel_path))
            elif len(path_parts) >= 3 and path_parts[0].isdigit():
                filename = path_parts[-1]
                uncategorized.append((filename, rel_path))

    # 카테고리별 출력
    for category in sorted(categorized):
        index_lines.extend(render_entries(category, categorized[category]))

    if uncategorized:
        index_lines.extend(render_entries("uncategorized", uncategorized))

    # === 링크 파일 인덱싱 ===
    link_files = [
        f for f in os.listdir(BASE_DIR)
        if f.endswith("-Links.md") and os.path.isfile(os.path.join(BASE_DIR, f))
    ]

    if link_files:
        index_lines.append("\n## 🔗 Links")
        for f in sorted(link_files):
            label = f.replace("-Links.md", "")
            index_lines.append(f"- [{label}]({f})")

    # README.md 저장
    readme_path = os.path.join(BASE_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write("\n".join(index_lines))

    print(f"✅ README.md updated with {len(index_lines)} lines (excluding .gitignore matches).")

def save_to_git(commit_message: str):
    print(f"📦 Git 저장 중: '{commit_message}'")

    cmds = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push", "origin", "main"]
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"❌ 실패: {' '.join(cmd)}")
            print(result.stderr.strip())
            sys.exit(1)
        else:
            print(f"✅ 완료: {' '.join(cmd)}")

def add_link_to_monthly_links_file(url: str, date_str: str = None, tag: str = None, title: str = None):
    from datetime import datetime

    today = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    date = today.strftime("%Y-%m-%d")
    filename = today.strftime("%Y-%m-Links.md")
    filepath = os.path.join(BASE_DIR, filename)

    # entry 구성
    entry_text = f"[{title}]({url})" if title else url
    if tag:
        entry_text += f" `#{tag}`"
    new_entry = f"- [ ] {entry_text}"
    header_line = f"#### {date}"

    if not os.path.exists(filepath):
        # 파일이 아예 없는 경우
        with open(filepath, "w") as f:
            f.write(f"{header_line}\n{new_entry}\n")
        print(f"📎 Created new link file and added: {url}")
        return

    # 파일 있는 경우: 읽기
    with open(filepath, "r") as f:
        lines = f.readlines()

    found_date_section = False
    already_exists = False
    inserted = False
    new_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 날짜 헤더 도달
        if stripped == header_line:
            found_date_section = True
            new_lines.append(line)
            continue

        # 다른 날짜 헤더를 만났다면 현재 섹션 종료
        if found_date_section and stripped.startswith("#### "):
            if not already_exists:
                new_lines.append(new_entry + "\n")
                inserted = True
            found_date_section = False

        # 중복 체크: 링크 주소 기준
        if found_date_section and url in stripped:
            already_exists = True

        new_lines.append(line)

    # 파일 끝에 추가할 경우
    if found_date_section and not already_exists and not inserted:
        new_lines.append(new_entry + "\n")

    # 날짜 섹션이 아예 없었던 경우 → 새 섹션 추가
    if not found_date_section and not inserted and not already_exists:
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines.append("\n")
        new_lines.append(f"{header_line}\n{new_entry}\n")

    with open(filepath, "w") as f:
        f.writelines(new_lines)

    print("✅ Link already exists." if already_exists else f"📎 Added: " + url)


def interactive_find():
    import subprocess
    import pathspec

    print("🔍 Launching interactive file finder (fzf)...")

    # .gitignore 로딩
    def load_gitignore_patterns(base_dir: str):
        gitignore_path = os.path.join(base_dir, ".gitignore")
        if not os.path.exists(gitignore_path):
            return pathspec.PathSpec.from_lines("gitwildmatch", [])
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)

    spec = load_gitignore_patterns(BASE_DIR)
    IGNORED_DIRS = {"venv", ".git", "__pycache__", ".mypy_cache"}

    # 전체 파일 목록 추출
    candidates = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            if not file.endswith(".md") or file == "README.md":
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BASE_DIR)
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
            target = os.path.join(BASE_DIR, selected)
            print(f"📂 Opening: {target}")
            subprocess.run(["code", target])
        else:
            print("❌ Nothing selected.")
    except FileNotFoundError:
        print("❌ fzf is not installed. Try: brew install fzf")

from datetime import datetime

def generate_til_zip(from_date_str: str, to_date_str: str):
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    assert from_date <= to_date

    collected = []

    for root, _, files in os.walk(BASE_DIR):
        for file in sorted(files):
            if not file.endswith(".md"):
                continue
            if file == "README.md" or "Links" in file or "zip-" in file:
                continue

            try:
                date_part = file.replace(".md", "")
                date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except:
                continue  # 파일명이 날짜 형식이 아닌 경우 무시

            if from_date <= date <= to_date:
                rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
                category = os.path.basename(os.path.dirname(rel_path))
                with open(os.path.join(BASE_DIR, rel_path), "r") as f:
                    content = f.read().strip()
                collected.append((date, category, rel_path, content))

    if not collected:
        print("📭 해당 기간에 해당하는 TIL 파일이 없습니다.")
        return

    output_file = f"zip-{from_date_str}_to_{to_date_str}.md"
    output_path = os.path.join(BASE_DIR, output_file)

    with open(output_path, "w") as f:
        f.write(f"# 📦 TIL ZIP: {from_date_str} → {to_date_str}\n\n")
        for date, category, path, content in sorted(collected):
            f.write(f"## 📁 {category} / {date}\n")
            f.write(f"*File: `{path}`*\n\n")
            f.write(content + "\n\n---\n\n")

    print(f"✅ 압축 파일 생성 완료: {output_file}")

def generate_current_month_zip():
    from datetime import datetime

    today = datetime.today()
    target_year = today.year
    target_month = today.month

    collected = []

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if not file.endswith(".md") or "Links" in file or "zip-" in file:
                continue

            try:
                date_part = file.replace(".md", "")
                date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except ValueError:
                continue  # 무시

            if date.year == target_year and date.month == target_month:
                rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
                category = os.path.basename(os.path.dirname(rel_path))
                with open(os.path.join(BASE_DIR, rel_path), "r") as f:
                    content = f.read().strip()
                collected.append((date, category, rel_path, content))

    if not collected:
        print("📭 이번 달에 작성된 TIL이 없습니다.")
        return

    filename = f"zip-{target_year}-{str(target_month).zfill(2)}.md"
    output_path = os.path.join(BASE_DIR, filename)

    with open(output_path, "w") as f:
        f.write(f"# 📦 TIL ZIP: {target_year}-{str(target_month).zfill(2)}\n\n")
        for date, category, rel_path, content in sorted(collected):
            f.write(f"## 📁 {category} / {date}\n")
            f.write(f"*File: `{rel_path}`*\n\n")
            f.write(content + "\n\n---\n\n")

    print(f"✅ 월간 ZIP 생성 완료: {filename}")

# -------------------------------
# 3. 명령어 라우팅
# -------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="📝 TIL (Today I Learned) CLI - 기록, 검색, 인덱싱, 링크 관리, 요약 ZIP까지 한 번에!",
        epilog="""
    예시:
    til note android               # 오늘 날짜로 android TIL 생성
    til note --date 2025-07-01     # 날짜 지정 생성
    til search coroutine           # 전체 TIL에서 'coroutine' 검색
    til link "https://..."         # 링크 추가
    til find                       # fzf로 TIL 파일 검색 및 열기
    til zip --from ... --to ...    # 날짜 범위 TIL 파일 ZIP
    til zip                        # 이번 달 TIL ZIP 생성
    til save "feat: commit msg"    # git add/commit/push 자동화
    til index                      # README 인덱스 및 설명 자동 생성
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # note
    note_parser = subparsers.add_parser("note", help="오늘 또는 지정 날짜에 TIL 생성")
    note_parser.add_argument("category", nargs="?", default=None, help="주제명 (예: android)")
    note_parser.add_argument("--date", type=str, help="날짜 지정 (형식: YYYY-MM-DD)")

    # search
    search_parser = subparsers.add_parser(
        "search", help="전체 TIL에서 키워드 검색 (본문 내에서 강조 표시됨)"
    )
    search_parser.add_argument("keyword", type=str, help="검색할 키워드")

    # index
    subparsers.add_parser(
        "index", help="README.md 인덱스를 자동 생성 (카테고리별 정리 + collapse 지원)"
    )

    # save
    save_parser = subparsers.add_parser(
        "save", help="Git add → commit → push 순으로 변경사항 저장"
    )
    save_parser.add_argument("message", type=str, help="Git 커밋 메시지")   

    # link
    link_parser = subparsers.add_parser("link", help="Links.md에 링크 추가")
    link_parser.add_argument("url", type=str, help="추가할 링크")
    link_parser.add_argument("--date", type=str, help="날짜 지정 (형식: YYYY-MM-DD)")
    link_parser.add_argument("--tag", type=str, help="태그 (예: kotlin)")
    link_parser.add_argument("--title", type=str, help="링크에 붙일 제목")

    # find 
    subparsers.add_parser("find", help="fzf로 모든 TIL 파일을 검색하고 열기")

    # zip 
    zip_parser = subparsers.add_parser("zip", help="TIL 파일을 zip 형식으로 요약")
    zip_parser.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    zip_parser.add_argument("--to", dest="to_date", help="끝 날짜 (YYYY-MM-DD)")

    # 명령 실행
    args = parser.parse_args()

    if args.command == "note":
        category = args.category or DEFAULT_CATEGORY
        if not category:
            print("❌ category를 명시하거나 .tilrc에 default_category를 설정해주세요.")
            sys.exit(1)
        create_or_open_note(category, args.date)
    elif args.command == "search":
        search_notes(args.keyword)
    elif args.command == "index":
        update_index()
    elif args.command == "save":
        save_to_git(args.message)
    elif args.command == "link":
        final_tag = args.tag or DEFAULT_LINK_TAG
        final_title = args.title or args.url  # 기본 title은 링크 자체
        add_link_to_monthly_links_file(
            url=args.url,
            date_str=args.date,
            tag=final_tag,
            title=final_title
        )

        if OPEN_BROWSER:
            subprocess.run(["open", args.url])
    elif args.command == "find":
        interactive_find()
    elif args.command == "zip":
        if args.from_date and args.to_date:
            generate_til_zip(args.from_date, args.to_date)
        else:
            generate_current_month_zip()


# -------------------------------
# 4. 진입점
# -------------------------------
if __name__ == "__main__":
    main()