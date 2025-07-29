import unittest
import tempfile
import subprocess
import os
from unittest.mock import patch, MagicMock
import sys

# Fix the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.git_operations import save_to_git

class TestGitOperations(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    def test_save_to_git_success(self, mock_subprocess):
        """Test successful git save operation."""
        # Mock successful subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        save_to_git(self.test_dir, "test commit message")
        
        # Should call git add, commit, and push
        self.assertEqual(mock_subprocess.call_count, 3)
        
        # Check the commands
        calls = mock_subprocess.call_args_list
        self.assertEqual(calls[0][0][0], ["git", "add", "."])
        self.assertEqual(calls[1][0][0], ["git", "commit", "-m", "test commit message"])
        self.assertEqual(calls[2][0][0], ["git", "push", "origin", "main"])
        
        # Check cwd parameter
        for call in calls:
            self.assertEqual(call[1]["cwd"], self.test_dir)
    
    @patch('subprocess.run')
    @patch('sys.exit')
    def test_save_to_git_failure(self, mock_exit, mock_subprocess):
        """Test git save operation failure."""
        # Mock failed subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "git error message"
        mock_subprocess.return_value = mock_result
        
        # Make sys.exit actually raise SystemExit to stop execution
        mock_exit.side_effect = SystemExit(1)
        
        with self.assertRaises(SystemExit):
            save_to_git(self.test_dir, "test commit message")
        
        # Should exit with error code 1
        mock_exit.assert_called_with(1)
        
        # Should only call git add (first command that fails)
        self.assertEqual(mock_subprocess.call_count, 1)
        
        # Verify it was the git add command that was called
        calls = mock_subprocess.call_args_list
        self.assertEqual(calls[0][0][0], ["git", "add", "."])

if __name__ == '__main__':
    unittest.main()
