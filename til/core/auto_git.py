#!/usr/bin/env python3
"""
자동 Git 관리 모듈
정해진 시간에 자동으로 변경사항을 감지하고 Git에 커밋/푸시하는 기능을 제공합니다.
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import platform


class AutoGitManager:
    """자동 Git 관리 클래스"""
    
    def __init__(self, base_dir: str):
        """
        자동 Git 관리자 초기화
        
        Args:
            base_dir: TIL 기본 디렉토리
        """
        self.base_dir = base_dir
        self.config_file = os.path.join(base_dir, ".auto_git_config.json")
        self._load_config()
    
    def _load_config(self):
        """설정 파일 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {}
            # 빈 설정 파일 생성
            self._save_config()
    
    def _save_config(self):
        """설정 파일 저장"""
        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def check_git_status(self) -> Tuple[bool, List[str]]:
        """
        Git 상태를 확인하여 변경사항이 있는지 검사합니다.
        
        Returns:
            (변경사항_존재_여부, 변경된_파일_목록)
        """
        try:
            # git status --porcelain으로 변경사항 확인
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                return False, []
            
            # 변경된 파일 목록 추출
            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # git status --porcelain 형식: "XY PATH"
                    # XY는 상태 코드, PATH는 파일 경로
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    # 무시할 파일들 필터링
                    if not self._should_ignore_file(file_path):
                        changed_files.append(file_path)
            
            return len(changed_files) > 0, changed_files
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 상태 확인 실패: {e}")
            return False, []
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False, []
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """
        파일이 무시해야 할 파일인지 확인합니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            무시 여부
        """
        # 무시할 파일 패턴들
        ignore_patterns = [
            '.auto_git_config.json',  # 설정 파일 자체
            '.DS_Store',              # macOS 시스템 파일
            '*.log',                  # 로그 파일
            '__pycache__/',           # Python 캐시
            '.git/',                  # Git 디렉토리
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_path:
                return True
        
        # 와일드카드 패턴 처리
        if '*.log' in ignore_patterns and file_path.endswith('.log'):
            return True
        
        return False
    
    def generate_commit_message(self, changed_files: List[str]) -> str:
        """
        변경사항을 기반으로 커밋 메시지를 생성합니다.
        
        Args:
            changed_files: 변경된 파일 목록
            
        Returns:
            생성된 커밋 메시지
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not changed_files:
            return f"📝 Daily TIL update - {today} (no changes)"
        
        # 카테고리별로 파일 분류
        categories = set()
        for file_path in changed_files:
            # 파일 경로에서 카테고리 추출 (예: android/2025-01-20.md -> android)
            parts = file_path.split('/')
            if len(parts) > 1 and not parts[0].startswith('.'):
                categories.add(parts[0])
        
        if categories:
            category_list = ', '.join(sorted(categories))
            return f"📝 Daily TIL update - {today} ({category_list})"
        else:
            return f"📝 Daily TIL update - {today} ({len(changed_files)} files changed)"
    
    def auto_commit_and_push(self, custom_message: Optional[str] = None) -> bool:
        """
        변경사항을 자동으로 커밋하고 푸시합니다.
        
        Args:
            custom_message: 사용자 정의 커밋 메시지 (선택사항)
            
        Returns:
            성공 여부
        """
        try:
            # 변경사항 확인
            has_changes, changed_files = self.check_git_status()
            
            if not has_changes:
                print("📝 변경사항이 없습니다.")
                return True
            
            # 커밋 메시지 생성
            if custom_message:
                commit_message = custom_message
            else:
                commit_message = self.generate_commit_message(changed_files)
            
            print(f"📦 자동 Git 저장 중: '{commit_message}'")
            print(f"📄 변경된 파일: {len(changed_files)}개")
            
            # Git 명령어 실행 (push는 선택적)
            commands = [
                ["git", "add", "."],
                ["git", "commit", "-m", commit_message]
            ]
            
            # 원격 저장소가 있는 경우에만 push 실행
            try:
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True
                )
                stdout_text = result.stdout if isinstance(result.stdout, str) else ""
                if result.returncode == 0 and stdout_text.strip():
                    commands.append(["git", "push", "origin", "main"])
            except:
                pass  # push 실패해도 커밋은 성공으로 간주
            
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"❌ 실패: {' '.join(cmd)}")
                    print(result.stderr.strip())
                    return False
                else:
                    print(f"✅ 완료: {' '.join(cmd)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 자동 커밋 실패: {e}")
            return False
    
    def setup_schedule(self, time: str, message: str = "") -> bool:
        """
        시스템 스케줄러에 자동 커밋 작업을 등록합니다.
        
        Args:
            time: 실행 시간 (HH:MM 형식)
            message: 커밋 메시지 (선택사항)
            
        Returns:
            성공 여부
        """
        try:
            # 시간 형식 검증
            hour, minute = map(int, time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("잘못된 시간 형식입니다. HH:MM 형식을 사용하세요.")
            
            # 설정 저장
            self.config['auto_git'] = {
                'enabled': True,
                'time': time,
                'message': message,
                'created_at': datetime.now().isoformat()
            }
            self._save_config()
            
            # 플랫폼별 스케줄러 설정
            if platform.system() == "Darwin":  # macOS
                return self._setup_macos_schedule(time)
            elif platform.system() == "Linux":
                return self._setup_linux_schedule(time)
            elif platform.system() == "Windows":
                return self._setup_windows_schedule(time)
            else:
                print(f"❌ 지원하지 않는 플랫폼: {platform.system()}")
                return False
                
        except Exception as e:
            print(f"❌ 스케줄 설정 실패: {e}")
            return False
    
    def _setup_macos_schedule(self, time: str) -> bool:
        """macOS에서 launchd를 사용한 스케줄 설정"""
        try:
            hour, minute = map(int, time.split(':'))
            
            # plist 파일 생성
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.til.autogit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>til</string>
        <string>auto</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.base_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/til_autogit.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/til_autogit_error.log</string>
</dict>
</plist>"""
            
            # plist 파일 저장
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.til.autogit.plist")
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # launchd에 등록
            subprocess.run(["launchctl", "load", plist_path], check=True)
            
            print(f"✅ macOS 스케줄 설정 완료: 매일 {time}에 실행")
            return True
            
        except Exception as e:
            print(f"❌ macOS 스케줄 설정 실패: {e}")
            return False
    
    def _setup_linux_schedule(self, time: str) -> bool:
        """Linux에서 cron을 사용한 스케줄 설정"""
        try:
            hour, minute = map(int, time.split(':'))
            
            # cron 명령어 생성
            cron_command = f"{minute} {hour} * * * cd {self.base_dir} && til auto run"
            
            # 현재 사용자의 crontab에 추가
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # 이미 존재하는지 확인
            if "til auto run" not in current_crontab:
                new_crontab = current_crontab.strip() + "\n" + cron_command + "\n"
                
                # 임시 파일에 저장
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(new_crontab)
                    temp_file = f.name
                
                # crontab 업데이트
                subprocess.run(["crontab", temp_file], check=True)
                os.unlink(temp_file)
            
            print(f"✅ Linux 스케줄 설정 완료: 매일 {time}에 실행")
            return True
            
        except Exception as e:
            print(f"❌ Linux 스케줄 설정 실패: {e}")
            return False
    
    def _setup_windows_schedule(self, time: str) -> bool:
        """Windows에서 Task Scheduler를 사용한 스케줄 설정"""
        try:
            hour, minute = map(int, time.split(':'))
            
            # PowerShell 스크립트 생성
            script_content = f"""cd "{self.base_dir}"
til auto run"""
            
            script_path = os.path.join(self.base_dir, "auto_git_task.ps1")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Task Scheduler 명령어
            task_name = "TIL_AutoGit"
            command = f'schtasks /create /tn "{task_name}" /tr "powershell.exe -ExecutionPolicy Bypass -File \\"{script_path}\\"" /sc daily /st {hour:02d}:{minute:02d} /f'
            
            subprocess.run(command, shell=True, check=True)
            
            print(f"✅ Windows 스케줄 설정 완료: 매일 {time}에 실행")
            return True
            
        except Exception as e:
            print(f"❌ Windows 스케줄 설정 실패: {e}")
            return False
    
    def remove_schedule(self) -> bool:
        """
        등록된 스케줄을 제거합니다.
        
        Returns:
            성공 여부
        """
        try:
            # 설정 제거
            if 'auto_git' in self.config:
                del self.config['auto_git']
                self._save_config()
            
            # 플랫폼별 스케줄 제거
            if platform.system() == "Darwin":  # macOS
                plist_path = os.path.expanduser("~/Library/LaunchAgents/com.til.autogit.plist")
                if os.path.exists(plist_path):
                    subprocess.run(["launchctl", "unload", plist_path])
                    os.remove(plist_path)
                    
            elif platform.system() == "Linux":
                # crontab에서 til auto run 제거
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    filtered_lines = [line for line in lines if "til auto run" not in line]
                    
                    if filtered_lines != lines:
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                            f.write('\n'.join(filtered_lines) + '\n')
                            temp_file = f.name
                        
                        subprocess.run(["crontab", temp_file])
                        os.unlink(temp_file)
                        
            elif platform.system() == "Windows":
                subprocess.run(['schtasks', '/delete', '/tn', 'TIL_AutoGit', '/f'], 
                             capture_output=True)
            
            print("✅ 스케줄 제거 완료")
            return True
            
        except Exception as e:
            print(f"❌ 스케줄 제거 실패: {e}")
            return False
    
    def get_status(self) -> Dict:
        """
        현재 자동 Git 설정 상태를 반환합니다.
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'enabled': False,
            'time': None,
            'message': None,
            'platform': platform.system(),
            'config_file': self.config_file
        }
        
        if 'auto_git' in self.config:
            auto_git_config = self.config['auto_git']
            status.update({
                'enabled': auto_git_config.get('enabled', False),
                'time': auto_git_config.get('time'),
                'message': auto_git_config.get('message'),
                'created_at': auto_git_config.get('created_at')
            })
        
        return status


def format_status_output(status: Dict) -> str:
    """
    상태 정보를 포맷팅된 문자열로 변환합니다.
    
    Args:
        status: 상태 정보 딕셔너리
        
    Returns:
        포맷팅된 상태 문자열
    """
    if not status['enabled']:
        return "❌ 자동 Git 기능이 비활성화되어 있습니다."
    
    output = [
        "🤖 자동 Git 설정 상태",
        "=" * 30,
        f"✅ 활성화: {'예' if status['enabled'] else '아니오'}",
        f"⏰ 실행 시간: {status['time']}",
        f"💬 커밋 메시지: {status['message'] or '(자동 생성)'}",
        f"🖥️  플랫폼: {status['platform']}",
        f"📁 설정 파일: {status['config_file']}",
        f"📅 생성일: {status.get('created_at', '알 수 없음')}"
    ]
    
    return '\n'.join(output)
