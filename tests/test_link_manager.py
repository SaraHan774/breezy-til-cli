import unittest
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'til'))

from core.link_manager import add_link_to_monthly_links_file

class TestLinkManager(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_add_link_new_file(self):
        """Test adding link to a new monthly file."""
        url = "https://example.com"
        date_str = "2025-01-15"
        
        add_link_to_monthly_links_file(
            self.test_dir, url, date_str, tag="test", title="Example"
        )
        
        expected_file = os.path.join(self.test_dir, "2025-01-Links.md")
        self.assertTrue(os.path.exists(expected_file))
        
        with open(expected_file, "r") as f:
            content = f.read()
            self.assertIn("#### 2025-01-15", content)
            self.assertIn("[Example](https://example.com) `#test`", content)
            self.assertIn("- [ ]", content)
    
    def test_add_link_existing_file_same_date(self):
        """Test adding link to existing file on same date."""
        # Create initial file
        links_file = os.path.join(self.test_dir, "2025-01-Links.md")
        with open(links_file, "w") as f:
            f.write("#### 2025-01-15\n- [ ] [First](https://first.com)\n")
        
        add_link_to_monthly_links_file(
            self.test_dir, "https://second.com", "2025-01-15", title="Second"
        )
        
        with open(links_file, "r") as f:
            content = f.read()
            self.assertIn("[First](https://first.com)", content)
            self.assertIn("[Second](https://second.com)", content)
            self.assertEqual(content.count("#### 2025-01-15"), 1)
    
    def test_add_duplicate_link(self):
        """Test adding duplicate link (should not duplicate)."""
        # Create initial file
        links_file = os.path.join(self.test_dir, "2025-01-Links.md")
        with open(links_file, "w") as f:
            f.write("#### 2025-01-15\n- [ ] https://example.com\n")
        
        add_link_to_monthly_links_file(
            self.test_dir, "https://example.com", "2025-01-15"
        )
        
        with open(links_file, "r") as f:
            content = f.read()
            # Should only appear once
            self.assertEqual(content.count("https://example.com"), 1)
    
    def test_add_link_new_date_section(self):
        """Test adding link with new date section."""
        # Create initial file
        links_file = os.path.join(self.test_dir, "2025-01-Links.md")
        with open(links_file, "w") as f:
            f.write("#### 2025-01-10\n- [ ] [Old](https://old.com)\n")
        
        add_link_to_monthly_links_file(
            self.test_dir, "https://new.com", "2025-01-15", title="New"
        )
        
        with open(links_file, "r") as f:
            content = f.read()
            self.assertIn("#### 2025-01-10", content)
            self.assertIn("#### 2025-01-15", content)
            self.assertIn("[Old](https://old.com)", content)
            self.assertIn("[New](https://new.com)", content)

if __name__ == '__main__':
    unittest.main()
