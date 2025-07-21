#!/usr/bin/env python3
"""
Input Detection Module
Detects and validates input types (markdown folder vs XML file)
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

def detect_input_type(input_path):
    """
    Detect if input is a markdown folder or XML file
    
    Args:
        input_path (str or Path): Path to input (file or directory)
        
    Returns:
        str: 'markdown' or 'xml'
        
    Raises:
        ValueError: If input type cannot be determined
    """
    path = Path(input_path)
    
    if not path.exists():
        raise ValueError(f"Input path does not exist: {input_path}")
    
    if path.is_file():
        # Check if it's an XML file
        if path.suffix.lower() == '.xml':
            return 'xml'
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}. Only .xml files are supported.")
    
    elif path.is_dir():
        # Check if directory contains markdown files
        md_files = list(path.rglob("*.md"))
        if md_files:
            return 'markdown'
        else:
            raise ValueError(f"No markdown files found in directory: {input_path}")
    
    else:
        raise ValueError(f"Input path is neither a file nor directory: {input_path}")

def validate_markdown_folder(folder_path):
    """
    Validate markdown folder structure
    
    Args:
        folder_path (str or Path): Path to markdown folder
        
    Returns:
        dict: Validation results with file count and structure info
        
    Raises:
        ValueError: If folder is invalid
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    # Find all markdown files recursively
    md_files = list(folder.rglob("*.md"))
    
    if not md_files:
        raise ValueError(f"No markdown files found in: {folder_path}")
    
    # Analyze folder structure
    structure = {
        'total_files': len(md_files),
        'files': [],
        'subdirectories': set()
    }
    
    for file_path in md_files:
        relative_path = file_path.relative_to(folder)
        structure['files'].append({
            'name': file_path.name,
            'path': str(relative_path),
            'size': file_path.stat().st_size
        })
        
        # Track subdirectories
        if relative_path.parent != Path('.'):
            structure['subdirectories'].add(str(relative_path.parent))
    
    structure['subdirectories'] = list(structure['subdirectories'])
    
    logger.info(f"Markdown folder validated: {structure['total_files']} files found")
    return structure

def validate_xml_file(xml_path):
    """
    Validate XML file structure
    
    Args:
        xml_path (str or Path): Path to XML file
        
    Returns:
        dict: Validation results with XML structure info
        
    Raises:
        ValueError: If XML file is invalid
    """
    xml_file = Path(xml_path)
    
    if not xml_file.exists():
        raise ValueError(f"XML file does not exist: {xml_path}")
    
    if not xml_file.is_file():
        raise ValueError(f"Path is not a file: {xml_path}")
    
    if xml_file.suffix.lower() != '.xml':
        raise ValueError(f"File is not an XML file: {xml_path}")
    
    try:
        # Try to parse XML to validate structure
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Analyze XML structure
        structure = {
            'root_tag': root.tag,
            'attributes': dict(root.attrib),
            'total_elements': len(list(root.iter())),
            'file_size': xml_file.stat().st_size
        }
        
        # Count different element types
        element_counts = {}
        for elem in root.iter():
            element_counts[elem.tag] = element_counts.get(elem.tag, 0) + 1
        
        structure['element_counts'] = element_counts
        
        logger.info(f"XML file validated: {structure['total_elements']} elements found")
        return structure
        
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML file: {e}")
    except Exception as e:
        raise ValueError(f"Error reading XML file: {e}")

def get_input_info(input_path):
    """
    Get comprehensive information about input
    
    Args:
        input_path (str or Path): Path to input
        
    Returns:
        dict: Input type and validation info
    """
    try:
        input_type = detect_input_type(input_path)
        
        if input_type == 'markdown':
            validation = validate_markdown_folder(input_path)
        else:  # xml
            validation = validate_xml_file(input_path)
        
        return {
            'type': input_type,
            'path': str(input_path),
            'validation': validation
        }
        
    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        raise 