import unittest
import tempfile
import os
import json
import subprocess
from unittest.mock import patch, MagicMock
import sys

# Fix the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.auto_git import AutoGitManager, format_status_output


class TestAutoGitManager(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.auto_manager = AutoGitManager(self.test_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_init_creates_config_file(self):
        """Test that AutoGitManager creates config file on initialization."""
        config_file = os.path.join(self.test_dir, ".auto_git_config.json")
        self.assertTrue(os.path.exists(config_file))
    
    def test_load_config_empty(self):
        """Test loading empty config."""
        self.assertEqual(self.auto_manager.config, {})
    
    def test_save_and_load_config(self):
        """Test saving and loading config."""
        test_config = {"test": "value"}
        self.auto_manager.config = test_config
        self.auto_manager._save_config()
        
        # Create new instance to test loading
        new_manager = AutoGitManager(self.test_dir)
        self.assertEqual(new_manager.config, test_config)
    
    def test_should_ignore_file(self):
        """Test file ignore patterns."""
        # Should ignore
        self.assertTrue(self.auto_manager._should_ignore_file('.auto_git_config.json'))
        self.assertTrue(self.auto_manager._should_ignore_file('.DS_Store'))
        self.assertTrue(self.auto_manager._should_ignore_file('test.log'))
        self.assertTrue(self.auto_manager._should_ignore_file('__pycache__/test.pyc'))
        self.assertTrue(self.auto_manager._should_ignore_file('.git/config'))
        
        # Should not ignore
        self.assertFalse(self.auto_manager._should_ignore_file('android/2025-01-20.md'))
        self.assertFalse(self.auto_manager._should_ignore_file('python/README.md'))
    
    def test_generate_commit_message_no_changes(self):
        """Test commit message generation with no changes."""
        message = self.auto_manager.generate_commit_message([])
        self.assertIn("no changes", message)
    
    def test_generate_commit_message_with_categories(self):
        """Test commit message generation with category files."""
        changed_files = [
            'android/2025-01-20.md',
            'kotlin/2025-01-20.md',
            'python/2025-01-20.md'
        ]
        message = self.auto_manager.generate_commit_message(changed_files)
        self.assertIn("android, kotlin, python", message)
    
    def test_generate_commit_message_with_files(self):
        """Test commit message generation with general files."""
        changed_files = [
            'README.md',
            'config.txt',
            'data.json'
        ]
        message = self.auto_manager.generate_commit_message(changed_files)
        self.assertIn("3 files changed", message)
    
    @patch('subprocess.run')
    def test_check_git_status_no_changes(self, mock_subprocess):
        """Test git status check with no changes."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_subprocess.return_value = mock_result
        
        has_changes, changed_files = self.auto_manager.check_git_status()
        
        self.assertFalse(has_changes)
        self.assertEqual(changed_files, [])
    
    @patch('subprocess.run')
    def test_check_git_status_with_changes(self, mock_subprocess):
        """Test git status check with changes."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "M  android/2025-01-20.md\nA  kotlin/2025-01-20.md"
        mock_subprocess.return_value = mock_result
        
        has_changes, changed_files = self.auto_manager.check_git_status()
        
        self.assertTrue(has_changes)
        self.assertEqual(len(changed_files), 2)
        self.assertIn('android/2025-01-20.md', changed_files)
        self.assertIn('kotlin/2025-01-20.md', changed_files)
    
    @patch('subprocess.run')
    def test_auto_commit_and_push_success(self, mock_subprocess):
        """Test successful auto commit and push."""
        # Mock git status with changes
        status_result = MagicMock()
        status_result.returncode = 0
        status_result.stdout = "M  android/2025-01-20.md"
        
        # Mock successful git commands
        git_result = MagicMock()
        git_result.returncode = 0
        
        mock_subprocess.side_effect = [status_result, git_result, git_result, git_result]
        
        success = self.auto_manager.auto_commit_and_push()
        self.assertTrue(success)
        
        # Should call git add, commit, and push
        self.assertEqual(mock_subprocess.call_count, 4)
    
    @patch('subprocess.run')
    def test_auto_commit_and_push_no_changes(self, mock_subprocess):
        """Test auto commit with no changes."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_subprocess.return_value = mock_result
        
        success = self.auto_manager.auto_commit_and_push()
        self.assertTrue(success)
        
        # Should only call git status, not add/commit/push
        self.assertEqual(mock_subprocess.call_count, 1)
    
    def test_setup_schedule_invalid_time(self):
        """Test setup schedule with invalid time format."""
        success = self.auto_manager.setup_schedule("25:00")
        self.assertFalse(success)
        
        success = self.auto_manager.setup_schedule("12:60")
        self.assertFalse(success)
        
        success = self.auto_manager.setup_schedule("invalid")
        self.assertFalse(success)
    
    def test_get_status_default(self):
        """Test getting status with default config."""
        status = self.auto_manager.get_status()
        
        self.assertFalse(status['enabled'])
        self.assertIsNone(status['time'])
        self.assertIsNone(status['message'])
        self.assertIn('platform', status)
        self.assertIn('config_file', status)
    
    def test_get_status_with_config(self):
        """Test getting status with configured auto git."""
        self.auto_manager.config['auto_git'] = {
            'enabled': True,
            'time': '20:00',
            'message': 'Test message',
            'created_at': '2025-01-20T10:00:00'
        }
        
        status = self.auto_manager.get_status()
        
        self.assertTrue(status['enabled'])
        self.assertEqual(status['time'], '20:00')
        self.assertEqual(status['message'], 'Test message')
        self.assertEqual(status['created_at'], '2025-01-20T10:00:00')


class TestFormatStatusOutput(unittest.TestCase):
    
    def test_format_status_disabled(self):
        """Test formatting status when auto git is disabled."""
        status = {
            'enabled': False,
            'time': None,
            'message': None,
            'platform': 'Darwin',
            'config_file': '/test/.auto_git_config.json'
        }
        
        output = format_status_output(status)
        self.assertIn("비활성화", output)
    
    def test_format_status_enabled(self):
        """Test formatting status when auto git is enabled."""
        status = {
            'enabled': True,
            'time': '20:00',
            'message': 'Test message',
            'platform': 'Darwin',
            'config_file': '/test/.auto_git_config.json',
            'created_at': '2025-01-20T10:00:00'
        }
        
        output = format_status_output(status)
        self.assertIn("활성화", output)
        self.assertIn("20:00", output)
        self.assertIn("Test message", output)
        self.assertIn("Darwin", output)


if __name__ == '__main__':
    unittest.main()
