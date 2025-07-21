#!/usr/bin/env python3
"""
Parser Module
Handles parsing of both markdown files and XML files into a common internal format
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger

def parse_markdown_content(content, file_id):
    """
    Parse markdown content and convert to internal structure
    
    Args:
        content (str): Markdown content
        file_id (str): File identifier
        
    Returns:
        list: List of sections with hierarchical structure
    """
    lines = content.split('\n')
    sections = []
    current_section = None
    current_subsection = None
    current_subsubsection = None
    current_content = []
    
    for line in lines:
        # Check for headers
        if line.strip().startswith('#'):
            # Save previous content
            if current_content:
                if current_subsubsection:
                    current_subsubsection['content'] = '\n'.join(current_content)
                elif current_subsection:
                    current_subsection['content'] = '\n'.join(current_content)
                elif current_section:
                    current_section['content'] = '\n'.join(current_content)
                current_content = []
            
            # Parse header level and numbering
            header_level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            
            # Extract numbering and title
            number_match = re.match(r'(\d+\.\d+(?:\.\d+)*)\s+(.+)', header_text)
            if number_match:
                number = number_match.group(1)
                title = number_match.group(2)
            else:
                # If no numbering, use the text as title
                number = None
                title = header_text
            
            if header_level == 1:  # Main section
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'number': number,
                    'title': title,
                    'level': 1,
                    'subsections': [],
                    'content': ''
                }
                current_subsection = None
                current_subsubsection = None
                
            elif header_level == 2:  # Subsection
                # If we don't have a current section, create one
                if not current_section:
                    current_section = {
                        'number': None,
                        'title': 'Main Content',
                        'level': 1,
                        'subsections': [],
                        'content': ''
                    }
                
                if current_subsection:
                    current_section['subsections'].append(current_subsection)
                current_subsection = {
                    'number': number,
                    'title': title,
                    'level': 2,
                    'subsubsections': [],
                    'content': ''
                }
                current_subsubsection = None
                
            elif header_level == 3:  # Sub-subsection
                # If we don't have a current section, create one
                if not current_section:
                    current_section = {
                        'number': None,
                        'title': 'Main Content',
                        'level': 1,
                        'subsections': [],
                        'content': ''
                    }
                
                # If we don't have a current subsection, create one
                if not current_subsection:
                    current_subsection = {
                        'number': None,
                        'title': 'Subsection',
                        'level': 2,
                        'subsubsections': [],
                        'content': ''
                    }
                
                if current_subsubsection:
                    current_subsection['subsubsections'].append(current_subsubsection)
                current_subsubsection = {
                    'number': number,
                    'title': title,
                    'level': 3,
                    'content': ''
                }
                
        else:
            # Regular content line
            current_content.append(line)
    
    # Save final content
    if current_content:
        if current_subsubsection:
            current_subsubsection['content'] = '\n'.join(current_content)
        elif current_subsection:
            current_subsection['content'] = '\n'.join(current_content)
        elif current_section:
            current_section['content'] = '\n'.join(current_content)
    
    # Add final sections
    if current_subsubsection and current_subsection:
        current_subsection['subsubsections'].append(current_subsubsection)
    if current_subsection and current_section:
        current_section['subsections'].append(current_subsection)
    if current_section:
        sections.append(current_section)
    
    return sections

def parse_xml_file(file_path):
    """
    Parse XML file and convert to internal structure
    
    Args:
        file_path (str or Path): Path to XML file
        
    Returns:
        dict: Internal data structure
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract metadata
        metadata = {
            'name': root.get('name', 'Unknown'),
            'version': root.get('version', '1.0'),
            'processed_at': root.get('processed_at', ''),
            'source_folder': root.get('source_folder', '')
        }
        
        # Parse structure
        files = []
        
        for folder_elem in root.findall('folder'):
            for file_elem in folder_elem.findall('file'):
                file_data = {
                    'id': file_elem.get('id', ''),
                    'name': file_elem.get('name', ''),
                    'path': file_elem.get('path', ''),
                    'sections': []
                }
                
                # Parse sections
                for section_elem in file_elem.findall('section'):
                    section_data = {
                        'id': section_elem.get('id', ''),
                        'title': section_elem.get('title', ''),
                        'level': 1,
                        'content': '',
                        'subsections': []
                    }
                    
                    # Get content
                    content_elem = section_elem.find('content')
                    if content_elem is not None and content_elem.text:
                        section_data['content'] = content_elem.text.strip()
                    
                    # Parse subsections
                    for subsection_elem in section_elem.findall('subsection'):
                        subsection_data = {
                            'id': subsection_elem.get('id', ''),
                            'title': subsection_elem.get('title', ''),
                            'level': 2,
                            'content': '',
                            'subsubsections': []
                        }
                        
                        # Get content
                        content_elem = subsection_elem.find('content')
                        if content_elem is not None and content_elem.text:
                            subsection_data['content'] = content_elem.text.strip()
                        
                        # Parse sub-subsections
                        for subsubsection_elem in subsection_elem.findall('subsubsection'):
                            subsubsection_data = {
                                'id': subsubsection_elem.get('id', ''),
                                'title': subsubsection_elem.get('title', ''),
                                'level': 3,
                                'content': ''
                            }
                            
                            # Get content
                            content_elem = subsubsection_elem.find('content')
                            if content_elem is not None and content_elem.text:
                                subsubsection_data['content'] = content_elem.text.strip()
                            
                            subsection_data['subsubsections'].append(subsubsection_data)
                        
                        section_data['subsections'].append(subsection_data)
                    
                    file_data['sections'].append(section_data)
                
                files.append(file_data)
        
        return {
            'name': metadata['name'],
            'version': metadata['version'],
            'source_type': 'xml',
            'source_path': str(file_path),
            'files': files
        }
        
    except Exception as e:
        logger.error(f"Failed to parse XML file {file_path}: {e}")
        raise

def detect_folder_structure(folder_path):
    """
    Detect folder structure and collect metadata
    Skip the input folder level and start with subdirectories
    
    Args:
        folder_path (str or Path): Path to root folder
        
    Returns:
        list: List of folder objects with metadata
    """
    folder = Path(folder_path)
    folders = []
    
    # Get all subdirectories (excluding hidden folders)
    subdirs = [d for d in folder.iterdir() if d.is_dir() and not d.name.startswith('.')]
    subdirs.sort()  # Sort to maintain order
    
    for i, subdir in enumerate(subdirs, 1):
        # Extract folder ID and name from directory name
        folder_name = subdir.name
        
        # Try to extract numeric prefix for ordering
        order_match = re.match(r'(\d+)\.(.+)', folder_name)
        if order_match:
            folder_id = order_match.group(1)
            folder_name_clean = order_match.group(2)
            order = int(folder_id)
        else:
            folder_id = f"{i:02d}"
            folder_name_clean = folder_name
            order = i
        
        folder_data = {
            'id': folder_id,
            'name': folder_name_clean,
            'order': order,
            'path': str(subdir.relative_to(folder)),
            'files': []
        }
        
        folders.append(folder_data)
        logger.debug(f"Detected folder: {folder_name_clean} (ID: {folder_id}, Order: {order})")
    
    return folders

def parse_markdown_folder(folder_path, config=None):
    """
    Parse markdown folder and convert to internal structure with folder hierarchy
    Skip the input folder level and start with subdirectories
    
    Args:
        folder_path (str or Path): Path to markdown folder
        config (dict, optional): Configuration options
        
    Returns:
        dict: Internal data structure with folder hierarchy
    """
    folder = Path(folder_path)
    
    if config is None:
        config = {}
    
    # First, detect folder structure (subdirectories of input folder)
    folders = detect_folder_structure(folder_path)
    
    # Process files within each folder
    for folder_data in folders:
        folder_path_obj = folder / folder_data['path']
        
        # Find markdown files in this folder (recursively)
        md_files = list(folder_path_obj.rglob("*.md"))
        md_files.sort()
        
        for i, file_path in enumerate(md_files, 1):
            try:
                # Read markdown content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse content
                sections = parse_markdown_content(content, f"file_{i}")
                
                # Create file data - use relative path from the subfolder, not from input folder
                file_data = {
                    'id': f"{folder_data['id']}.{i:02d}",
                    'name': file_path.name,
                    'path': str(file_path.relative_to(folder_path_obj)),  # Relative to the subfolder itself
                    'sections': sections
                }
                
                folder_data['files'].append(file_data)
                logger.debug(f"Parsed markdown file: {file_path.name} in folder {folder_data['name']}")
                
            except Exception as e:
                logger.error(f"Failed to parse markdown file {file_path}: {e}")
                continue
    
    # Use the first subfolder name as the main name, or a generic name if multiple folders
    if len(folders) == 1:
        main_name = folders[0]['name']
    else:
        main_name = "Documentation"
    
    return {
        'name': main_name,
        'version': config.get('version', '1.0'),
        'source_type': 'markdown',
        'source_path': str(folder),
        'folders': folders
    }

def xml_to_internal_format(xml_data):
    """
    Convert XML data to internal format (alias for parse_xml_file)
    
    Args:
        xml_data (str or Path): XML file path or data
        
    Returns:
        dict: Internal data structure
    """
    if isinstance(xml_data, (str, Path)):
        return parse_xml_file(xml_data)
    else:
        raise ValueError("xml_data must be a file path") 