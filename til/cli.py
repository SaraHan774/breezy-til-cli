#!/usr/bin/env python3

import os
import sys
import subprocess
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

# -------------------------------
# 1. 기본 설정
# -------------------------------
def setup_environment():
    print(f"📂 Working in TIL base directory: {BASE_DIR}")
    
    # pathspec 없는 경우에만 설치 (pipx 환경에서는 이미 설치되어 있음)
    try:
        import pathspec
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS], check=True)

# -------------------------------
# 2. 모듈 임포트
# -------------------------------
from til.core.config import TILConfig
from til.core.file_operations import create_or_open_note, search_notes, interactive_find
from til.core.index_generator import update_index
from til.core.link_manager import add_link_to_monthly_links_file
from til.core.zip_generator import generate_til_zip, generate_current_month_zip
from til.core.git_operations import save_to_git

# -------------------------------
# 3. 명령어 라우팅
# -------------------------------
def main():
    # 환경 설정
    setup_environment()
    
    # 설정 로드
    config = TILConfig(BASE_DIR)
    
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
        category = args.category or config.default_category
        if not category:
            print("❌ category를 명시하거나 .tilrc에 default_category를 설정해주세요.")
            sys.exit(1)
        create_or_open_note(BASE_DIR, category, args.date, config.default_editor)
    elif args.command == "search":
        search_notes(BASE_DIR, args.keyword)
    elif args.command == "index":
        update_index(BASE_DIR)
    elif args.command == "save":
        save_to_git(BASE_DIR, args.message)
    elif args.command == "link":
        final_tag = args.tag or config.default_link_tag
        final_title = args.title or args.url  # 기본 title은 링크 자체
        add_link_to_monthly_links_file(
            BASE_DIR,
            url=args.url,
            date_str=args.date,
            tag=final_tag,
            title=final_title
        )

        if config.open_browser:
            subprocess.run(["open", args.url])
    elif args.command == "find":
        interactive_find(BASE_DIR, config.default_editor)
    elif args.command == "zip":
        if args.from_date and args.to_date:
            generate_til_zip(BASE_DIR, args.from_date, args.to_date)
        else:
            generate_current_month_zip(BASE_DIR)

# -------------------------------
# 4. 진입점
# -------------------------------
if __name__ == "__main__":
    main()