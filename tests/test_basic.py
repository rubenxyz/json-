#!/usr/bin/env python3
"""
Basic unit tests for the markdown to XML converter.

Tests cover:
- Parser module functionality
- XML generator functionality
- Basic integration scenarios
"""

import unittest
import tempfile
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock

# Import the modules to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import clean_text_for_xml, parse_markdown_content, detect_folder_structure
from xml_generator import create_xml_element, create_xml_document, write_xml_file, process_markdown_file


class TestParser(unittest.TestCase):
    """Test cases for the parser module."""
    
    def test_clean_text_for_xml_basic(self):
        """Test basic XML text cleaning."""
        # Test basic special characters
        self.assertEqual(clean_text_for_xml("Hello & World"), "Hello &amp; World")
        self.assertEqual(clean_text_for_xml("x < y > z"), "x &lt; y &gt; z")
        self.assertEqual(clean_text_for_xml('"quoted"'), "&quot;quoted&quot;")
        self.assertEqual(clean_text_for_xml("'apostrophe'"), "&apos;apostrophe&apos;")
        
        # Test non-string inputs
        self.assertEqual(clean_text_for_xml(123), "123")
        self.assertEqual(clean_text_for_xml(None), "None")
        
        # Test empty string
        self.assertEqual(clean_text_for_xml(""), "")
    
    def test_parse_markdown_content_basic(self):
        """Test basic markdown parsing."""
        content = """# Getting Started

Welcome to our documentation.

## 1.1 Introduction

This is the introduction content.

## 1.2 Installation

### 1.2.1 Prerequisites

Install Python 3.7+.

### 1.2.2 Setup

Run the setup script.

## 1.3 Usage

Basic usage instructions here."""
        
        sections = parse_markdown_content(content, "test.md")
        
        # Should have 2 sections: H1 and H2 (since H2 is treated as main section when no H1 subsections)
        self.assertEqual(len(sections), 2)
        
        # Check first section (H1)
        self.assertEqual(sections[0]['title'], 'Getting Started')
        self.assertIsNone(sections[0]['number'])
        self.assertEqual(sections[0]['content'].strip(), 'Welcome to our documentation.')
        
        # Check second section (H2) - it will be the last H2 section processed
        self.assertEqual(sections[1]['title'], 'Usage')
        self.assertEqual(sections[1]['number'], '1.3')
        self.assertEqual(sections[1]['content'].strip(), 'Basic usage instructions here.')
        
        # Check subsections in second section
        self.assertEqual(len(sections[1]['subsections']), 0)  # No subsections in Usage section

    def test_parse_markdown_content_empty(self):
        """Test parsing empty content."""
        sections = parse_markdown_content("", "test.md")
        self.assertEqual(len(sections), 0)
    
    def test_parse_markdown_content_invalid_input(self):
        """Test parsing with invalid input."""
        with self.assertRaises(ValueError):
            parse_markdown_content(123, "test.md")
        
        with self.assertRaises(ValueError):
            parse_markdown_content("content", "")
    
    def test_parse_markdown_content_no_numbering(self):
        """Test parsing markdown without numbered sections."""
        content = """# Getting Started

Welcome to our documentation.

## Introduction

This guide will help you get started.

### Prerequisites

- Python 3.7+
- Basic knowledge of markdown"""
        
        sections = parse_markdown_content(content, "test.md")
        
        # Should have 2 sections: H1 and H2
        self.assertEqual(len(sections), 2)
        
        # Check first section (H1)
        self.assertEqual(sections[0]['title'], 'Getting Started')
        self.assertIsNone(sections[0]['number'])
        self.assertEqual(sections[0]['content'].strip(), 'Welcome to our documentation.')
        
        # Check second section (H2)
        self.assertEqual(sections[1]['title'], 'Introduction')
        self.assertIsNone(sections[1]['number'])
        self.assertEqual(sections[1]['content'].strip(), 'This guide will help you get started.')
        
        # Check subsection
        self.assertEqual(len(sections[1]['subsections']), 1)
        self.assertEqual(sections[1]['subsections'][0]['title'], 'Prerequisites')
        self.assertIsNone(sections[1]['subsections'][0]['number'])
    
    def test_detect_folder_structure(self):
        """Test folder structure detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test folders
            folders = ['folder1', 'folder2', 'another-folder']
            for folder in folders:
                os.makedirs(os.path.join(temp_dir, folder))
            
            # Test detection
            result = detect_folder_structure(temp_dir)
            
            # Should detect all folders
            self.assertEqual(len(result), 3)
            self.assertIn('folder1', result)
            self.assertIn('folder2', result)
            self.assertIn('another-folder', result)
            
            # Should assign IDs in alphabetical order
            self.assertEqual(result['another-folder'], '01')
            self.assertEqual(result['folder1'], '02')
            self.assertEqual(result['folder2'], '03')


class TestXMLGenerator(unittest.TestCase):
    """Test cases for the XML generator module."""
    
    def test_create_xml_element_basic(self):
        """Test basic XML element creation."""
        root = ET.Element('root')
        element = create_xml_element(root, 'test', 'Hello & World', id='1')
        
        self.assertEqual(element.tag, 'test')
        self.assertEqual(element.text, 'Hello &amp; World')
        self.assertEqual(element.get('id'), '1')
    
    def test_create_xml_element_invalid_input(self):
        """Test XML element creation with invalid input."""
        root = ET.Element('root')
        
        # Test invalid tag
        with self.assertRaises(ValueError):
            create_xml_element(root, '', 'text')
        
        with self.assertRaises(ValueError):
            create_xml_element(root, None, 'text')
    
    def test_create_xml_element_with_special_chars(self):
        """Test XML element creation with special characters."""
        root = ET.Element('root')
        element = create_xml_element(root, 'test', '<script>alert("xss")</script>')
        
        self.assertEqual(element.text, '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;')
    
    def test_create_xml_document_basic(self):
        """Test XML document creation."""
        config = {
            'documentation_name': 'Test Documentation',
            'version': '2.0'
        }
        
        root = create_xml_document('test-folder', config, '2025-01-20_14-30-25')
        
        self.assertEqual(root.tag, 'documentation')
        self.assertEqual(root.get('name'), 'Test Documentation')
        self.assertEqual(root.get('version'), '2.0')
        self.assertEqual(root.get('processed_at'), '2025-01-20_14-30-25')
        self.assertEqual(root.get('source_folder'), 'test-folder')
    
    def test_create_xml_document_defaults(self):
        """Test XML document creation with default values."""
        root = create_xml_document('test-folder', {}, '2025-01-20_14-30-25')
        
        self.assertEqual(root.get('name'), 'test-folder')
        self.assertEqual(root.get('version'), '1.0')
    
    def test_write_xml_file(self):
        """Test XML file writing."""
        root = ET.Element('test')
        child = ET.SubElement(root, 'child')
        child.text = 'Hello World'
        
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            write_xml_file(root, tmp_path)
            
            # Verify file was created and contains content
            self.assertTrue(tmp_path.exists())
            
            # Read and verify content
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('<test>', content)
                self.assertIn('<child>Hello World</child>', content)
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_write_xml_file_invalid_input(self):
        """Test XML file writing with invalid input."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            with self.assertRaises(OSError):
                write_xml_file(None, tmp_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestIntegration(unittest.TestCase):
    """Test cases for integration scenarios."""
    
    def test_end_to_end_simple(self):
        """Test a simple end-to-end conversion."""
        content = """# Getting Started

Welcome to our documentation.

## Introduction

This guide will help you get started.

### Prerequisites

- Python 3.7+
- Basic knowledge of markdown"""
        
        # Test parsing
        sections = parse_markdown_content(content, "test.md")
        
        # Should have 2 sections (H1 and H2)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]['title'], 'Getting Started')
        
        # Test XML generation
        root = ET.Element('documentation')
        file_elem = ET.SubElement(root, 'file', id='01.01', name='test.md')
        
        # Add sections to XML
        for section in sections:
            section_elem = ET.SubElement(file_elem, 'section',
                                       id=section.get('number', ''),
                                       title=section.get('title', ''),
                                       level='2')
            
            if section.get('content'):
                content_elem = ET.SubElement(section_elem, 'content')
                content_elem.text = section['content']
        
        # Verify XML structure
        self.assertEqual(len(file_elem.findall('section')), 2)
        section = file_elem.find('section')
        self.assertEqual(section.get('title'), 'Getting Started')
        self.assertEqual(section.get('level'), '2')
    
    def test_error_handling(self):
        """Test error handling in the workflow."""
        # Test processing non-existent file
        root = ET.Element('folder')
        result = process_markdown_file(Path('does_not_exist.md'), '01.01', root, {})
        self.assertFalse(result)


def run_tests():
    """Run all tests."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestParser))
    suite.addTests(loader.loadTestsFromTestCase(TestXMLGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1) 