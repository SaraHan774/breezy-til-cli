import os
from datetime import datetime

def add_link_to_monthly_links_file(base_dir: str, url: str, date_str: str = None, tag: str = None, title: str = None, preview_text: str = None):
    """Add a link to monthly links file.

    preview_text가 제공되면 같은 줄 끝에 1줄 설명을 덧붙인다.
    """
    today = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.today()
    date = today.strftime("%Y-%m-%d")
    filename = today.strftime("%Y-%m-Links.md")
    filepath = os.path.join(base_dir, filename)

    # entry 구성
    entry_text = f"[{title}]({url})" if title else url
    if tag:
        entry_text += f" `#{tag}`"
    if preview_text:
        # 설명은 1줄만 사용하고 과도하게 길면 생략 처리한다.
        snippet = " ".join(preview_text.strip().splitlines())
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        entry_text += f" — {snippet}"
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
