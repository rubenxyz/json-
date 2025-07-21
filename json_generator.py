#!/usr/bin/env python3
"""
JSON Generator Module
Converts internal data structures to JSON output optimized for LLM parsing
"""

import json
from datetime import datetime
from pathlib import Path
from loguru import logger

def convert_to_json_format(internal_data):
    """
    Convert internal data structure to JSON format
    
    Args:
        internal_data (dict): Internal data structure from parser
        
    Returns:
        dict: JSON-formatted data
    """
    json_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '2.0',
            'format': 'json',
            'optimized_for': 'llm_parsing'
        },
        'documentation': {
            'name': internal_data.get('name', 'Unknown'),
            'version': internal_data.get('version', '1.0'),
            'source_type': internal_data.get('source_type', 'unknown'),
            'source_path': internal_data.get('source_path', ''),
            'total_files': len(internal_data.get('files', [])),
            'total_sections': 0
        },
        'content': {
            'files': []
        }
    }
    
    # Process files
    for file_data in internal_data.get('files', []):
        file_json = {
            'id': file_data.get('id', ''),
            'name': file_data.get('name', ''),
            'path': file_data.get('path', ''),
            'sections': []
        }
        
        # Process sections
        for section in file_data.get('sections', []):
            section_json = {
                'id': section.get('id', ''),
                'title': section.get('title', ''),
                'level': section.get('level', 1),
                'content': section.get('content', ''),
                'subsections': []
            }
            
            # Process subsections
            for subsection in section.get('subsections', []):
                subsection_json = {
                    'id': subsection.get('id', ''),
                    'title': subsection.get('title', ''),
                    'level': subsection.get('level', 2),
                    'content': subsection.get('content', ''),
                    'subsubsections': []
                }
                
                # Process sub-subsections
                for subsubsection in subsection.get('subsubsections', []):
                    subsubsection_json = {
                        'id': subsubsection.get('id', ''),
                        'title': subsubsection.get('title', ''),
                        'level': subsubsection.get('level', 3),
                        'content': subsubsection.get('content', '')
                    }
                    subsection_json['subsubsections'].append(subsubsection_json)
                
                section_json['subsections'].append(subsection_json)
            
            file_json['sections'].append(section_json)
            json_data['documentation']['total_sections'] += 1
        
        json_data['content']['files'].append(file_json)
    
    return json_data

def create_json_document(data, config=None):
    """
    Create JSON document with proper structure and formatting
    
    Args:
        data (dict): Data to convert to JSON
        config (dict, optional): Configuration options
        
    Returns:
        str: Formatted JSON string
    """
    if config is None:
        config = {}
    
    # Convert to JSON format
    json_data = convert_to_json_format(data)
    
    # Apply configuration options
    indent = config.get('indent', 2)
    sort_keys = config.get('sort_keys', False)
    ensure_ascii = config.get('ensure_ascii', False)
    
    # Generate JSON string
    json_string = json.dumps(
        json_data, 
        indent=indent, 
        sort_keys=sort_keys, 
        ensure_ascii=ensure_ascii,
        separators=(',', ': ') if indent else (',', ':')
    )
    
    return json_string

def write_json_file(json_data, output_path, config=None):
    """
    Write JSON data to file
    
    Args:
        json_data (str or dict): JSON data to write
        output_path (str or Path): Output file path
        config (dict, optional): Configuration options
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If json_data is a dict, convert to JSON string
        if isinstance(json_data, dict):
            # Apply configuration options
            indent = config.get('indent', 2) if config else 2
            sort_keys = config.get('sort_keys', False) if config else False
            ensure_ascii = config.get('ensure_ascii', False) if config else False
            
            # Generate JSON string
            json_string = json.dumps(
                json_data, 
                indent=indent, 
                sort_keys=sort_keys, 
                ensure_ascii=ensure_ascii,
                separators=(',', ': ') if indent else (',', ':')
            )
        else:
            json_string = json_data
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_string)
        
        logger.info(f"JSON file written: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write JSON file {output_path}: {e}")
        return False

def create_llm_optimized_json(internal_data, config=None):
    """
    Create JSON optimized specifically for LLM parsing with folder structure
    
    Args:
        internal_data (dict): Internal data structure with folder hierarchy
        config (dict, optional): Configuration options
        
    Returns:
        dict: LLM-optimized JSON structure with folder organization
    """
    if config is None:
        config = {}
    
    # LLM-optimized structure with folder hierarchy
    llm_json = {
        'instructions': {
            'format': 'json',
            'version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'source': internal_data.get('source_type', 'unknown'),
            'total_instructions': 0
        },
        'folders': []
    }
    
    # Process folder structure
    section_counter = 0
    
    for folder_data in internal_data.get('folders', []):
        folder_json = {
            'id': folder_data.get('id', ''),
            'name': folder_data.get('name', ''),
            'order': folder_data.get('order', 0),
            'files': []
        }
        
        # Process files within this folder
        for file_data in folder_data.get('files', []):
            file_json = {
                'id': file_data.get('id', ''),
                'name': file_data.get('name', ''),
                'path': file_data.get('path', ''),
                'sections': []
            }
            
            # Process sections within this file
            for section in file_data.get('sections', []):
                section_counter += 1
                
                # Main section
                llm_section = {
                    'id': f"{section_counter}",
                    'type': 'section',
                    'title': section.get('title', ''),
                    'content': section.get('content', ''),
                    'file': file_data.get('name', ''),
                    'folder': folder_data.get('name', ''),
                    'subsections': []
                }
                
                # Subsections
                for subsection in section.get('subsections', []):
                    section_counter += 1
                    
                    llm_subsection = {
                        'id': f"{section_counter}",
                        'type': 'subsection',
                        'title': subsection.get('title', ''),
                        'content': subsection.get('content', ''),
                        'parent_section': section.get('title', ''),
                        'file': file_data.get('name', ''),
                        'folder': folder_data.get('name', ''),
                        'subsubsections': []
                    }
                    
                    # Sub-subsections
                    for subsubsection in subsection.get('subsubsections', []):
                        section_counter += 1
                        
                        llm_subsubsection = {
                            'id': f"{section_counter}",
                            'type': 'subsubsection',
                            'title': subsubsection.get('title', ''),
                            'content': subsubsection.get('content', ''),
                            'parent_subsection': subsection.get('title', ''),
                            'parent_section': section.get('title', ''),
                            'file': file_data.get('name', ''),
                            'folder': folder_data.get('name', '')
                        }
                        
                        llm_subsection['subsubsections'].append(llm_subsubsection)
                    
                    llm_section['subsections'].append(llm_subsection)
                
                file_json['sections'].append(llm_section)
            
            folder_json['files'].append(file_json)
        
        llm_json['folders'].append(folder_json)
    
    llm_json['instructions']['total_instructions'] = section_counter
    
    return llm_json 