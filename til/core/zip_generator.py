import os
from datetime import datetime

def generate_til_zip(base_dir: str, from_date_str: str, to_date_str: str):
    """Generate a ZIP file for a date range."""
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    assert from_date <= to_date

    collected = []

    for root, _, files in os.walk(base_dir):
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
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                category = os.path.basename(os.path.dirname(rel_path))
                with open(os.path.join(base_dir, rel_path), "r") as f:
                    content = f.read().strip()
                collected.append((date, category, rel_path, content))

    if not collected:
        print("📭 해당 기간에 해당하는 TIL 파일이 없습니다.")
        return

    output_file = f"zip-{from_date_str}_to_{to_date_str}.md"
    output_path = os.path.join(base_dir, output_file)

    with open(output_path, "w") as f:
        f.write(f"# 📦 TIL ZIP: {from_date_str} → {to_date_str}\n\n")
        for date, category, path, content in sorted(collected):
            f.write(f"## 📁 {category} / {date}\n")
            f.write(f"*File: `{path}`*\n\n")
            f.write(content + "\n\n---\n\n")

    print(f"✅ 압축 파일 생성 완료: {output_file}")

def generate_current_month_zip(base_dir: str):
    """Generate a ZIP file for the current month."""
    today = datetime.today()
    target_year = today.year
    target_month = today.month

    collected = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".md") or "Links" in file or "zip-" in file:
                continue

            try:
                date_part = file.replace(".md", "")
                date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except ValueError:
                continue  # 무시

            if date.year == target_year and date.month == target_month:
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                category = os.path.basename(os.path.dirname(rel_path))
                with open(os.path.join(base_dir, rel_path), "r") as f:
                    content = f.read().strip()
                collected.append((date, category, rel_path, content))

    if not collected:
        print("📭 이번 달에 작성된 TIL이 없습니다.")
        return

    filename = f"zip-{target_year}-{str(target_month).zfill(2)}.md"
    output_path = os.path.join(base_dir, filename)

    with open(output_path, "w") as f:
        f.write(f"# 📦 TIL ZIP: {target_year}-{str(target_month).zfill(2)}\n\n")
        for date, category, rel_path, content in sorted(collected):
            f.write(f"## 📁 {category} / {date}\n")
            f.write(f"*File: `{rel_path}`*\n\n")
            f.write(content + "\n\n---\n\n")

    print(f"✅ 월간 ZIP 생성 완료: {filename}")
