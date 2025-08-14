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
from til.core.streak_analyzer import get_streak_info, get_streak_info_with_visualization
from til.core.template_manager import TemplateManager, format_template_list
from til.core.auto_git import AutoGitManager, format_status_output

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
    note_parser.add_argument("--template", type=str, default="default", help="사용할 템플릿 (예: project, study, bugfix)")

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
    link_parser.add_argument("--preview", action="store_true", help="설명 1줄 미리보기 포함")

    # find 
    subparsers.add_parser("find", help="fzf로 모든 TIL 파일을 검색하고 열기")

    # zip 
    zip_parser = subparsers.add_parser("zip", help="TIL 파일을 zip 형식으로 요약")
    zip_parser.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    zip_parser.add_argument("--to", dest="to_date", help="끝 날짜 (YYYY-MM-DD)")

    # streak
    streak_parser = subparsers.add_parser("streak", help="학습 스트릭과 통계 확인")
    streak_parser.add_argument("--visual", action="store_true", help="시각화 포함 (잔디 + 주간 패턴)")
    streak_parser.add_argument("--grass-only", action="store_true", help="잔디만 표시")
    streak_parser.add_argument("--weekly-only", action="store_true", help="주간 패턴만 표시")

    # template
    template_parser = subparsers.add_parser("template", help="템플릿 관리")
    template_parser.add_argument("template_command", choices=["list", "create", "delete", "show"], help="템플릿 명령어")
    template_parser.add_argument("--id", type=str, help="템플릿 ID")
    template_parser.add_argument("--name", type=str, help="템플릿 이름")
    template_parser.add_argument("--description", type=str, help="템플릿 설명")
    template_parser.add_argument("--file", type=str, help="템플릿 내용 파일 경로")

    # auto (자동 Git 관리)
    auto_parser = subparsers.add_parser("auto", help="자동 Git 관리 (정해진 시간에 자동 커밋/푸시)")
    auto_parser.add_argument("auto_command", choices=["setup", "status", "remove", "run", "test"], help="자동화 명령어")
    auto_parser.add_argument("--time", type=str, help="실행 시간 (HH:MM 형식, 예: 20:00)")
    auto_parser.add_argument("--message", type=str, help="커밋 메시지 (선택사항)")

    # 명령 실행
    args = parser.parse_args()

    if args.command == "note":
        category = args.category or config.default_category
        if not category:
            print("❌ category를 명시하거나 .tilrc에 default_category를 설정해주세요.")
            sys.exit(1)
        create_or_open_note(BASE_DIR, category, args.date, config.default_editor, args.template)
    elif args.command == "search":
        search_notes(BASE_DIR, args.keyword)
    elif args.command == "index":
        update_index(BASE_DIR)
    elif args.command == "save":
        save_to_git(BASE_DIR, args.message)
    elif args.command == "link":
        final_tag = args.tag or config.default_link_tag
        final_title = args.title or args.url  # 기본 title은 링크 자체
        preview_text = None

        # --title 미지정이거나 --preview가 켜진 경우에만 메타 수집 시도 (실패는 조용히 폴백)
        if (args.title is None) or args.preview:
            try:
                from til.core.metadata import fetch_url_metadata
                meta = fetch_url_metadata(BASE_DIR, args.url)
                if args.title is None and meta.get("title"):
                    final_title = meta["title"]
                if args.preview and meta.get("description"):
                    preview_text = meta["description"]
            except Exception:
                pass

        add_link_to_monthly_links_file(
            BASE_DIR,
            url=args.url,
            date_str=args.date,
            tag=final_tag,
            title=final_title,
            preview_text=preview_text
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
    elif args.command == "streak":
        if args.visual:
            streak_info = get_streak_info_with_visualization(BASE_DIR, show_grass=True, show_weekly=True)
        elif args.grass_only:
            streak_info = get_streak_info_with_visualization(BASE_DIR, show_grass=True, show_weekly=False)
        elif args.weekly_only:
            streak_info = get_streak_info_with_visualization(BASE_DIR, show_grass=False, show_weekly=True)
        else:
            streak_info = get_streak_info(BASE_DIR)
        print(streak_info)
    elif args.command == "template":
        template_manager = TemplateManager(BASE_DIR)
        
        # 템플릿 하위 명령어 확인
        template_command = getattr(args, 'template_command', None)
        
        if template_command == "list":
            templates = template_manager.list_templates()
            print(format_template_list(templates))
        elif template_command == "show":
            if not args.id:
                print("❌ --id 옵션이 필요합니다.")
                sys.exit(1)
            try:
                templates = template_manager.list_templates()
                if args.id in templates:
                    content = templates[args.id]["content"]
                    print(f"📋 템플릿 '{args.id}' 내용:")
                    print("=" * 50)
                    print(content)
                else:
                    print(f"❌ 템플릿 '{args.id}'을 찾을 수 없습니다.")
            except Exception as e:
                print(f"❌ 템플릿을 찾을 수 없습니다: {e}")
        elif template_command == "create":
            if not all([args.id, args.name, args.description, args.file]):
                print("❌ --id, --name, --description, --file 옵션이 모두 필요합니다.")
                sys.exit(1)
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    content = f.read()
                template_manager.create_template(args.id, args.name, args.description, content)
                print(f"✅ 템플릿 '{args.id}'이 생성되었습니다.")
            except Exception as e:
                print(f"❌ 템플릿 생성 실패: {e}")
        elif template_command == "delete":
            if not args.id:
                print("❌ --id 옵션이 필요합니다.")
                sys.exit(1)
            try:
                template_manager.delete_template(args.id)
                print(f"✅ 템플릿 '{args.id}'이 삭제되었습니다.")
            except Exception as e:
                print(f"❌ 템플릿 삭제 실패: {e}")
        else:
            print("❌ 유효하지 않은 템플릿 명령어입니다. 'list', 'show', 'create', 'delete' 중 하나를 선택하세요.")
    elif args.command == "auto":
        auto_manager = AutoGitManager(BASE_DIR)
        
        if args.auto_command == "setup":
            if not args.time:
                print("❌ --time 옵션이 필요합니다. (예: --time 20:00)")
                sys.exit(1)
            
            success = auto_manager.setup_schedule(args.time, args.message or "")
            if success:
                print("✅ 자동 Git 설정이 완료되었습니다!")
                print(f"⏰ 매일 {args.time}에 자동으로 커밋/푸시됩니다.")
        elif args.auto_command == "status":
            status = auto_manager.get_status()
            print(format_status_output(status))
        elif args.auto_command == "remove":
            success = auto_manager.remove_schedule()
            if success:
                print("✅ 자동 Git 설정이 제거되었습니다.")
        elif args.auto_command == "run":
            # 스케줄러에서 호출되는 실제 실행 함수
            success = auto_manager.auto_commit_and_push()
            if success:
                print("✅ 자동 Git 작업이 완료되었습니다.")
            else:
                print("❌ 자동 Git 작업에 실패했습니다.")
                sys.exit(1)
        elif args.auto_command == "test":
            # 테스트 실행 (즉시 실행)
            print("🧪 자동 Git 기능을 테스트합니다...")
            success = auto_manager.auto_commit_and_push()
            if success:
                print("✅ 테스트가 성공했습니다!")
            else:
                print("❌ 테스트에 실패했습니다.")
                sys.exit(1)

# -------------------------------
# 4. 진입점
# -------------------------------
if __name__ == "__main__":
    main()