#!/usr/bin/env python3
"""
Test runner for TIL CLI.
Usage: python run_tests.py [test_module]

Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py test_config        # Run specific test module
    python run_tests.py -v                 # Run with verbose output
"""

import unittest
import sys
import os

def main():
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Set up test discovery
    loader = unittest.TestLoader()
    
    # Check for specific test module argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # Run specific test module
        test_module = sys.argv[1]
        if not test_module.startswith('tests.'):
            test_module = f'tests.{test_module}'
        
        try:
            suite = loader.loadTestsFromName(test_module)
        except Exception as e:
            print(f"❌ Error loading test module '{test_module}': {e}")
            sys.exit(1)
    else:
        # Run all tests
        test_dir = os.path.join(current_dir, 'tests')
        suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Set up test runner
    verbosity = 2 if '-v' in sys.argv or '--verbose' in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    
    print("🧪 Running TIL CLI tests...")
    print("=" * 50)
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("=" * 50)
    if result.wasSuccessful():
        print(f"✅ All tests passed! ({result.testsRun} tests)")
        sys.exit(0)
    else:
        failures = len(result.failures)
        errors = len(result.errors)
        print(f"❌ Tests failed: {failures} failures, {errors} errors out of {result.testsRun} tests")
        sys.exit(1)

if __name__ == '__main__':
    main()
