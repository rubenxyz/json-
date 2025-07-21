#!/usr/bin/env python3
"""
JSON Parser for JSON to HTML Explorer Tool
Parses JSON files and prepares data for HTML generation
"""

import json
from pathlib import Path
from loguru import logger

def parse_json_file(file_path, config=None):
    """
    Parse JSON file and prepare data for HTML generation
    
    Args:
        file_path (str or Path): Path to JSON file
        config (dict, optional): Configuration options
        
    Returns:
        dict: Parsed JSON data with metadata
    """
    if config is None:
        config = {}
    
    file_path = Path(file_path)
    
    try:
        # Read and parse JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Analyze the JSON structure
        structure_analysis = analyze_json_structure(json_data)
        
        # Prepare data for HTML generation
        processed_data = {
            'data': json_data,
            'metadata': {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'structure': structure_analysis,
                'root_type': type(json_data).__name__,
                'total_elements': count_elements(json_data)
            }
        }
        
        logger.info(f"JSON file parsed successfully: {file_path.name}")
        logger.info(f"Root type: {processed_data['metadata']['root_type']}")
        logger.info(f"Total elements: {processed_data['metadata']['total_elements']}")
        
        return processed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error parsing JSON file: {e}")
        raise

def analyze_json_structure(data, max_depth=10, current_depth=0):
    """
    Analyze JSON structure for HTML generation
    
    Args:
        data: JSON data to analyze
        max_depth: Maximum depth to analyze
        current_depth: Current depth in recursion
        
    Returns:
        dict: Structure analysis
    """
    if current_depth >= max_depth:
        return {
            'type': 'truncated',
            'depth': current_depth,
            'message': f'Structure truncated at depth {max_depth}'
        }
    
    if isinstance(data, dict):
        return {
            'type': 'object',
            'keys': list(data.keys()),
            'key_count': len(data),
            'has_nested': any(isinstance(v, (dict, list)) for v in data.values()),
            'children': {
                key: analyze_json_structure(value, max_depth, current_depth + 1)
                for key, value in data.items()
            } if current_depth < max_depth - 1 else None
        }
    elif isinstance(data, list):
        return {
            'type': 'array',
            'length': len(data),
            'has_nested': any(isinstance(item, (dict, list)) for item in data),
            'sample_items': [
                analyze_json_structure(item, max_depth, current_depth + 1)
                for item in data[:5]  # Sample first 5 items
            ] if data and current_depth < max_depth - 1 else None
        }
    else:
        return {
            'type': 'primitive',
            'value_type': type(data).__name__,
            'value_length': len(str(data)) if data is not None else 0,
            'is_long': len(str(data)) > 100 if data is not None else False
        }

def count_elements(data):
    """
    Count total number of elements in JSON data
    
    Args:
        data: JSON data to count
        
    Returns:
        int: Total element count
    """
    if isinstance(data, dict):
        return 1 + sum(count_elements(v) for v in data.values())
    elif isinstance(data, list):
        return 1 + sum(count_elements(item) for item in data)
    else:
        return 1

def prepare_tree_data(data, path="", max_depth=10, current_depth=0):
    """
    Prepare JSON data for tree view generation
    
    Args:
        data: JSON data
        path: Current path in the tree
        max_depth: Maximum depth to process
        current_depth: Current depth
        
    Returns:
        dict: Tree node data
    """
    if current_depth >= max_depth:
        return {
            'id': path or 'root',
            'name': '...',
            'type': 'truncated',
            'expanded': False,
            'children': []
        }
    
    if isinstance(data, dict):
        return {
            'id': path or 'root',
            'name': path.split('.')[-1] if '.' in path else 'root',
            'type': 'object',
            'expanded': current_depth < 2,  # Auto-expand first 2 levels
            'children': [
                prepare_tree_data(value, f"{path}.{key}" if path else key, 
                                max_depth, current_depth + 1)
                for key, value in data.items()
            ]
        }
    elif isinstance(data, list):
        return {
            'id': path or 'root',
            'name': path.split('.')[-1] if '.' in path else 'root',
            'type': 'array',
            'expanded': current_depth < 2,
            'children': [
                prepare_tree_data(item, f"{path}[{i}]" if path else f"[{i}]", 
                                max_depth, current_depth + 1)
                for i, item in enumerate(data)
            ]
        }
    else:
        return {
            'id': path or 'root',
            'name': path.split('.')[-1] if '.' in path else 'root',
            'type': 'primitive',
            'value': data,
            'expanded': False,
            'children': []
        }

def get_node_by_path(data, path):
    """
    Get JSON node by path (e.g., "user.profile.name" or "items[0].title")
    
    Args:
        data: JSON data
        path: Path to the node
        
    Returns:
        tuple: (node_data, node_path)
    """
    if not path or path == 'root':
        return data, 'root'
    
    current = data
    current_path = 'root'
    
    # Split path by dots and brackets
    import re
    parts = re.split(r'\.|\[|\]', path)
    parts = [p for p in parts if p]  # Remove empty strings
    
    for part in parts:
        if part.isdigit():
            # Array index
            if isinstance(current, list):
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                    current_path = f"{current_path}[{part}]"
                else:
                    return None, None
            else:
                return None, None
        else:
            # Object key
            if isinstance(current, dict) and part in current:
                current = current[part]
                current_path = f"{current_path}.{part}"
            else:
                return None, None
    
    return current, current_path

def format_value_for_display(value, max_length=200):
    """
    Format JSON value for display in HTML
    
    Args:
        value: Value to format
        max_length: Maximum length before truncation
        
    Returns:
        str: Formatted value
    """
    if value is None:
        return '<span class="null">null</span>'
    elif isinstance(value, bool):
        return f'<span class="boolean">{str(value).lower()}</span>'
    elif isinstance(value, (int, float)):
        return f'<span class="number">{value}</span>'
    elif isinstance(value, str):
        if len(value) > max_length:
            return f'<span class="string">"{value[:max_length]}..."</span>'
        else:
            return f'<span class="string">"{value}"</span>'
    else:
        return f'<span class="unknown">{str(value)}</span>' 