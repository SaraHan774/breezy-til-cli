import os
import pathspec

def render_entries(category: str, entries: list[tuple[str, str]]) -> list[str]:
    """Render entries for a category."""
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

def update_index(base_dir: str):
    """Update the README.md index file."""
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
        "- `til auto setup --time 20:00` → 매일 정해진 시간에 자동 커밋/푸시",
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

    spec = load_gitignore_patterns(base_dir)

    # 무시할 디렉토리 명시
    IGNORED_DIRS = {"venv", "__pycache__", ".pytest_cache", ".git", ".idea", ".mypy_cache", ".DS_Store"}

    # 파일 탐색
    for root, dirs, files in os.walk(base_dir):
        # 무시할 디렉토리 제외
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in sorted(files):
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)

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
        f for f in os.listdir(base_dir)
        if f.endswith("-Links.md") and os.path.isfile(os.path.join(base_dir, f))
    ]

    if link_files:
        index_lines.append("\n## 🔗 Links")
        for f in sorted(link_files):
            label = f.replace("-Links.md", "")
            index_lines.append(f"- [{label}]({f})")

    # README.md 저장
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("\n".join(index_lines))

    print(f"✅ README.md updated with {len(index_lines)} lines (excluding .gitignore matches).")
