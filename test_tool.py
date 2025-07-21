#!/usr/bin/env python3
"""
Test script for JSON to HTML Explorer Tool
Tests all major functionality including valid JSON, error handling, and edge cases
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from loguru import logger

# Import our modules
from input_detector import get_input_info, validate_json_file
from json_parser import parse_json_file
from html_generator import create_interactive_html, write_html_file

def setup_test_logging():
    """Setup logging for tests"""
    logger.remove()
    logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")

def test_valid_json():
    """Test with valid JSON file"""
    print("🧪 Testing valid JSON processing...")
    
    # Test with sample.json
    result = get_input_info("input/sample.json")
    
    if result['validation'] == 'valid':
        print("✅ Valid JSON detection working")
        
        # Test parsing
        try:
            parsed_data = parse_json_file("input/sample.json")
            print("✅ JSON parsing working")
            
            # Test HTML generation
            html_content = create_interactive_html(parsed_data)
            if html_content and len(html_content) > 1000:
                print("✅ HTML generation working")
            else:
                print("❌ HTML generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            return False
    else:
        print(f"❌ Valid JSON detection failed: {result['error']}")
        return False
    
    return True

def test_error_handling():
    """Test error handling with various invalid inputs"""
    print("\n🧪 Testing error handling...")
    
    test_cases = [
        ("input/invalid.json", "JSON_DECODE_ERROR"),
        ("input/nonexistent.json", "FILE_NOT_FOUND"),
        ("input_detector.py", "INVALID_EXTENSION"),
    ]
    
    all_passed = True
    
    for file_path, expected_error in test_cases:
        print(f"  Testing {file_path}...")
        result = get_input_info(file_path)
        
        if result['validation'] == 'error' and result.get('error_code') == expected_error:
            print(f"  ✅ {expected_error} correctly detected")
        else:
            print(f"  ❌ Expected {expected_error}, got {result.get('error_code', 'UNKNOWN')}")
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🧪 Testing edge cases...")
    
    # Test empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("")
        empty_file = f.name
    
    try:
        result = get_input_info(empty_file)
        if result.get('error_code') == 'EMPTY_FILE':
            print("✅ Empty file detection working")
        else:
            print("❌ Empty file detection failed")
            return False
    finally:
        os.unlink(empty_file)
    
    # Test large file simulation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "' + 'x' * 1000000 + '"}')  # ~1MB file
        large_file = f.name
    
    try:
        result = get_input_info(large_file)
        if result['validation'] == 'valid':
            print("✅ Large file handling working")
        else:
            print("❌ Large file handling failed")
            return False
    finally:
        os.unlink(large_file)
    
    return True

def test_html_output():
    """Test HTML output generation and file writing"""
    print("\n🧪 Testing HTML output...")
    
    # Create test data
    test_data = {
        "data": {
            "test_object": {
                "string": "test value",
                "number": 42,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "nested": {
                    "deep": "value"
                }
            }
        },
        "metadata": {
            "file_path": "test.json",
            "file_name": "test.json",
            "file_size": 100,
            "root_type": "dict",
            "total_elements": 10
        }
    }
    
    try:
        # Generate HTML
        html_content = create_interactive_html(test_data)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_html = f.name
        
        success = write_html_file(html_content, temp_html)
        
        if success and os.path.exists(temp_html):
            file_size = os.path.getsize(temp_html)
            if file_size > 1000:  # HTML should be substantial
                print("✅ HTML file generation and writing working")
                os.unlink(temp_html)
                return True
            else:
                print("❌ Generated HTML file too small")
                os.unlink(temp_html)
                return False
        else:
            print("❌ HTML file writing failed")
            return False
            
    except Exception as e:
        print(f"❌ HTML output test failed: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow from input to output"""
    print("\n🧪 Testing complete workflow...")
    
    try:
        # Run the main script
        import subprocess
        result = subprocess.run([
            sys.executable, "json_to_html.py", "input/sample.json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Complete workflow successful")
            
            # Check if output was created
            output_dirs = [d for d in Path("output").iterdir() if d.is_dir() and d.name != ".DS_Store"]
            if output_dirs:
                latest_output = max(output_dirs, key=lambda x: x.stat().st_mtime)
                html_files = list(latest_output.glob("*.html"))
                if html_files:
                    print(f"✅ Output HTML file created: {html_files[0]}")
                    return True
                else:
                    print("❌ No HTML output file found")
                    return False
            else:
                print("❌ No output directory created")
                return False
        else:
            print(f"❌ Workflow failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Workflow timed out")
        return False
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting JSON to HTML Explorer Tool Tests\n")
    
    setup_test_logging()
    
    tests = [
        ("Valid JSON Processing", test_valid_json),
        ("Error Handling", test_error_handling),
        ("Edge Cases", test_edge_cases),
        ("HTML Output", test_html_output),
        ("Complete Workflow", test_complete_workflow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! The tool is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 