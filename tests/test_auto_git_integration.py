#!/usr/bin/env python3
"""
자동 Git 기능 통합 테스트
실제 Git 저장소에서 자동화 기능이 제대로 작동하는지 테스트합니다.
"""

import unittest
import tempfile
import os
import subprocess
import time
import json
import shutil
from datetime import datetime
import sys

# Fix the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.auto_git import AutoGitManager, format_status_output


class TestAutoGitIntegration(unittest.TestCase):
    """자동 Git 기능 통합 테스트 클래스"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Git 저장소 초기화
        self._init_git_repo()
        
        # AutoGitManager 인스턴스 생성
        self.auto_manager = AutoGitManager(self.test_dir)
        
        print(f"\n🧪 테스트 디렉토리: {self.test_dir}")
    
    def tearDown(self):
        """테스트 환경 정리"""
        os.chdir(self.original_cwd)
        
        # 스케줄 제거 (설정된 경우)
        try:
            self.auto_manager.remove_schedule()
        except:
            pass
        
        # 테스트 디렉토리 삭제
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Git 저장소 초기화"""
        try:
            # Git 저장소 초기화
            subprocess.run(["git", "init"], check=True, capture_output=True)
            
            # 기본 사용자 설정
            subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
            
            # 초기 커밋 생성
            with open("README.md", "w") as f:
                f.write("# Test TIL Repository\n\nThis is a test repository for auto git functionality.")
            
            subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True)
            
            print("✅ Git 저장소 초기화 완료")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 저장소 초기화 실패: {e}")
            raise
    
    def _create_test_til_file(self, category: str, content: str = None):
        """테스트용 TIL 파일 생성"""
        if content is None:
            content = f"# TIL - {datetime.now().strftime('%Y-%m-%d')}\n\n## 학습 내용\n\n- 테스트 내용"
        
        # 카테고리 디렉토리 생성
        category_dir = os.path.join(self.test_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # TIL 파일 생성
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(category_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def _get_git_status(self):
        """Git 상태 확인"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.test_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def _get_git_log(self, count: int = 5):
        """Git 로그 확인"""
        result = subprocess.run(
            ["git", "log", f"--oneline", "-n", str(count)],
            cwd=self.test_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def test_01_config_file_creation(self):
        """설정 파일 생성 테스트"""
        print("\n📋 테스트 1: 설정 파일 생성")
        
        config_file = os.path.join(self.test_dir, ".auto_git_config.json")
        self.assertTrue(os.path.exists(config_file), "설정 파일이 생성되지 않았습니다.")
        
        # 설정 파일 내용 확인
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertEqual(config, {}, "초기 설정은 빈 딕셔너리여야 합니다.")
        print("✅ 설정 파일 생성 테스트 통과")
    
    def test_02_git_status_detection(self):
        """Git 상태 감지 테스트"""
        print("\n📋 테스트 2: Git 상태 감지")
        
        # 초기 상태 확인 (변경사항 없음)
        has_changes, changed_files = self.auto_manager.check_git_status()
        self.assertFalse(has_changes, "초기에는 변경사항이 없어야 합니다.")
        self.assertEqual(changed_files, [], "변경된 파일 목록이 비어있어야 합니다.")
        
        # 테스트 파일 생성
        test_file = self._create_test_til_file("python", "테스트 내용")
        
        # 변경사항 감지 확인
        has_changes, changed_files = self.auto_manager.check_git_status()
        self.assertTrue(has_changes, "파일 생성 후 변경사항이 감지되어야 합니다.")
        self.assertGreater(len(changed_files), 0, "변경된 파일이 있어야 합니다.")
        
        print(f"✅ 변경사항 감지: {len(changed_files)}개 파일")
        print("✅ Git 상태 감지 테스트 통과")
    
    def test_03_commit_message_generation(self):
        """커밋 메시지 생성 테스트"""
        print("\n📋 테스트 3: 커밋 메시지 생성")
        
        # 카테고리별 파일 생성
        self._create_test_til_file("android", "Android 학습 내용")
        self._create_test_til_file("kotlin", "Kotlin 학습 내용")
        self._create_test_til_file("python", "Python 학습 내용")
        
        # 변경사항 확인
        has_changes, changed_files = self.auto_manager.check_git_status()
        self.assertTrue(has_changes)
        
        # 커밋 메시지 생성
        message = self.auto_manager.generate_commit_message(changed_files)
        
        # 메시지 검증
        self.assertIn("Daily TIL update", message, "커밋 메시지에 'Daily TIL update'가 포함되어야 합니다.")
        self.assertIn("android", message.lower(), "Android 카테고리가 포함되어야 합니다.")
        self.assertIn("kotlin", message.lower(), "Kotlin 카테고리가 포함되어야 합니다.")
        self.assertIn("python", message.lower(), "Python 카테고리가 포함되어야 합니다.")
        
        print(f"✅ 생성된 메시지: {message}")
        print("✅ 커밋 메시지 생성 테스트 통과")
    
    def test_04_auto_commit_and_push(self):
        """자동 커밋 및 푸시 테스트"""
        print("\n📋 테스트 4: 자동 커밋 및 푸시")
        
        # 초기 커밋 수 확인
        initial_log = self._get_git_log()
        initial_commit_count = len(initial_log.split('\n'))
        
        # 테스트 파일 생성
        self._create_test_til_file("test", "자동 커밋 테스트")
        
        # 자동 커밋 실행
        success = self.auto_manager.auto_commit_and_push()
        self.assertTrue(success, "자동 커밋이 성공해야 합니다.")
        
        # 커밋 확인
        final_log = self._get_git_log()
        final_commit_count = len(final_log.split('\n'))
        
        self.assertGreater(final_commit_count, initial_commit_count, "새로운 커밋이 생성되어야 합니다.")
        
        # 커밋 메시지 확인
        self.assertIn("Daily TIL update", final_log, "커밋 로그에 'Daily TIL update'가 포함되어야 합니다.")
        
        print(f"✅ 커밋 수: {initial_commit_count} → {final_commit_count}")
        print("✅ 자동 커밋 및 푸시 테스트 통과")
    
    def test_05_no_changes_handling(self):
        """변경사항 없음 처리 테스트"""
        print("\n📋 테스트 5: 변경사항 없음 처리")
        
        # 테스트 파일 생성 후 커밋
        self._create_test_til_file("nochanges", "변경사항 없음 테스트")
        self.auto_manager.auto_commit_and_push()
        
        # 변경사항 없음 상태에서 다시 실행
        success = self.auto_manager.auto_commit_and_push()
        self.assertTrue(success, "변경사항이 없어도 성공해야 합니다.")
        
        # 불필요한 커밋이 생성되지 않았는지 확인
        log = self._get_git_log()
        commit_lines = log.split('\n')
        
        # 마지막 커밋이 이전 커밋인지 확인 (새로운 커밋이 생성되지 않았는지)
        self.assertGreaterEqual(len(commit_lines), 2, "최소 2개의 커밋이 있어야 합니다.")
        last_commit = commit_lines[0] if commit_lines else ""
        self.assertIn("nochanges", last_commit, "마지막 커밋이 이전 테스트의 커밋이어야 합니다.")
        
        print("✅ 변경사항 없음 처리 테스트 통과")
    
    def test_06_custom_commit_message(self):
        """커스텀 커밋 메시지 테스트"""
        print("\n📋 테스트 6: 커스텀 커밋 메시지")
        
        # 테스트 파일 생성
        self._create_test_til_file("custom", "커스텀 메시지 테스트")
        
        # 커스텀 메시지로 자동 커밋
        custom_message = "🎯 커스텀 테스트 커밋"
        success = self.auto_manager.auto_commit_and_push(custom_message)
        self.assertTrue(success, "커스텀 메시지로 커밋이 성공해야 합니다.")
        
        # 커밋 메시지 확인
        log = self._get_git_log()
        self.assertIn(custom_message, log, f"커밋 로그에 '{custom_message}'가 포함되어야 합니다.")
        
        print(f"✅ 커스텀 메시지: {custom_message}")
        print("✅ 커스텀 커밋 메시지 테스트 통과")
    
    def test_07_file_ignore_patterns(self):
        """파일 무시 패턴 테스트"""
        print("\n📋 테스트 7: 파일 무시 패턴")
        
        # 무시해야 할 파일들 생성
        ignore_files = [
            ".auto_git_config.json",
            ".DS_Store",
            "test.log",
            "__pycache__/test.pyc"
        ]
        
        for filename in ignore_files:
            filepath = os.path.join(self.test_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write("test content")
        
        # TIL 파일도 생성
        self._create_test_til_file("valid", "유효한 TIL 파일")
        
        # 변경사항 확인
        has_changes, changed_files = self.auto_manager.check_git_status()
        
        # 무시된 파일들이 변경사항에 포함되지 않았는지 확인
        for ignore_file in ignore_files:
            self.assertNotIn(ignore_file, changed_files, f"'{ignore_file}'는 무시되어야 합니다.")
        
        # 유효한 TIL 파일은 포함되어야 함
        self.assertIn("valid", str(changed_files), "유효한 TIL 파일은 포함되어야 합니다.")
        
        print(f"✅ 무시된 파일: {len(ignore_files)}개")
        print("✅ 파일 무시 패턴 테스트 통과")
    
    def test_08_schedule_configuration(self):
        """스케줄 설정 테스트"""
        print("\n📋 테스트 8: 스케줄 설정")
        
        # 유효한 시간으로 설정
        success = self.auto_manager.setup_schedule("20:00", "테스트 메시지")
        self.assertTrue(success, "스케줄 설정이 성공해야 합니다.")
        
        # 설정 상태 확인
        status = self.auto_manager.get_status()
        self.assertTrue(status['enabled'], "자동화가 활성화되어야 합니다.")
        self.assertEqual(status['time'], "20:00", "설정된 시간이 일치해야 합니다.")
        self.assertEqual(status['message'], "테스트 메시지", "설정된 메시지가 일치해야 합니다.")
        
        # 잘못된 시간 형식 테스트
        invalid_times = ["25:00", "12:60", "invalid"]
        for invalid_time in invalid_times:
            success = self.auto_manager.setup_schedule(invalid_time)
            self.assertFalse(success, f"잘못된 시간 '{invalid_time}'은 거부되어야 합니다.")
        
        print("✅ 스케줄 설정 테스트 통과")
    
    def test_09_schedule_removal(self):
        """스케줄 제거 테스트"""
        print("\n📋 테스트 9: 스케줄 제거")
        
        # 스케줄 설정
        self.auto_manager.setup_schedule("21:00", "제거 테스트")
        
        # 설정 상태 확인
        status = self.auto_manager.get_status()
        self.assertTrue(status['enabled'], "설정 후 활성화되어야 합니다.")
        
        # 스케줄 제거
        success = self.auto_manager.remove_schedule()
        self.assertTrue(success, "스케줄 제거가 성공해야 합니다.")
        
        # 제거 후 상태 확인
        status = self.auto_manager.get_status()
        self.assertFalse(status['enabled'], "제거 후 비활성화되어야 합니다.")
        self.assertIsNone(status['time'], "제거 후 시간이 None이어야 합니다.")
        self.assertIsNone(status['message'], "제거 후 메시지가 None이어야 합니다.")
        
        print("✅ 스케줄 제거 테스트 통과")
    
    def test_10_status_formatting(self):
        """상태 포맷팅 테스트"""
        print("\n📋 테스트 10: 상태 포맷팅")
        
        # 비활성화 상태 테스트
        status = self.auto_manager.get_status()
        output = format_status_output(status)
        self.assertIn("비활성화", output, "비활성화 상태가 표시되어야 합니다.")
        
        # 활성화 상태 테스트
        self.auto_manager.setup_schedule("22:00", "포맷팅 테스트")
        status = self.auto_manager.get_status()
        output = format_status_output(status)
        
        self.assertIn("활성화", output, "활성화 상태가 표시되어야 합니다.")
        self.assertIn("22:00", output, "설정된 시간이 표시되어야 합니다.")
        self.assertIn("포맷팅 테스트", output, "설정된 메시지가 표시되어야 합니다.")
        
        print("✅ 상태 포맷팅 테스트 통과")
    
    def test_11_integration_workflow(self):
        """통합 워크플로우 테스트"""
        print("\n📋 테스트 11: 통합 워크플로우")
        
        # 1. 스케줄 설정
        success = self.auto_manager.setup_schedule("23:00", "통합 테스트")
        self.assertTrue(success, "스케줄 설정이 성공해야 합니다.")
        
        # 2. 상태 확인
        status = self.auto_manager.get_status()
        self.assertTrue(status['enabled'], "자동화가 활성화되어야 합니다.")
        
        # 3. 파일 생성 및 자동 커밋
        self._create_test_til_file("workflow", "통합 워크플로우 테스트")
        success = self.auto_manager.auto_commit_and_push()
        self.assertTrue(success, "자동 커밋이 성공해야 합니다.")
        
        # 4. 커밋 확인
        log = self._get_git_log()
        self.assertIn("Daily TIL update", log, "자동 생성된 커밋이 있어야 합니다.")
        
        # 5. 스케줄 제거
        success = self.auto_manager.remove_schedule()
        self.assertTrue(success, "스케줄 제거가 성공해야 합니다.")
        
        # 6. 최종 상태 확인
        status = self.auto_manager.get_status()
        self.assertFalse(status['enabled'], "최종적으로 비활성화되어야 합니다.")
        
        print("✅ 통합 워크플로우 테스트 통과")
    
    def test_12_error_handling(self):
        """에러 처리 테스트"""
        print("\n📋 테스트 12: 에러 처리")
        
        # Git 명령어 실패 시뮬레이션 (잘못된 디렉토리)
        # 실제로는 잘못된 경로에서도 설정 파일 생성이 가능하도록 수정됨
        temp_dir = tempfile.mkdtemp()
        invalid_manager = AutoGitManager(temp_dir)
        
        # 변경사항 확인 시 에러 처리 (Git 저장소가 아닌 경우)
        has_changes, changed_files = invalid_manager.check_git_status()
        self.assertFalse(has_changes, "Git 저장소가 아닌 경우 변경사항이 없다고 판단해야 합니다.")
        self.assertEqual(changed_files, [], "Git 저장소가 아닌 경우 빈 파일 목록을 반환해야 합니다.")
        
        # 자동 커밋 시 에러 처리 (변경사항이 없으므로 성공으로 간주)
        success = invalid_manager.auto_commit_and_push()
        self.assertTrue(success, "변경사항이 없는 경우 성공을 반환해야 합니다.")
        
        # 정리
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("✅ 에러 처리 테스트 통과")


def run_integration_tests():
    """통합 테스트 실행"""
    print("🚀 자동 Git 기능 통합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAutoGitIntegration)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print(f"✅ 성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 실패: {len(result.failures)}")
    print(f"⚠️  에러: {len(result.errors)}")
    print(f"📈 총 테스트: {result.testsRun}")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n⚠️  에러가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 성공률: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 통합 테스트 실행
    success = run_integration_tests()
    
    if success:
        print("\n🎉 모든 통합 테스트가 성공했습니다!")
        print("✅ 자동 Git 기능이 정상적으로 작동합니다.")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        print("🔧 문제를 해결한 후 다시 테스트해주세요.")
    
    sys.exit(0 if success else 1)
