#!/usr/bin/env python3
"""
Input Detector for JSON to HTML Explorer Tool
Detects and validates JSON input files
"""

import json
from pathlib import Path
from loguru import logger

def get_input_info(input_path):
    """
    Detect and validate JSON input file
    
    Args:
        input_path (str or Path): Path to input file
        
    Returns:
        dict: Input information including type, validation status, and details
    """
    input_path = Path(input_path)
    
    # Check if path exists
    if not input_path.exists():
        return {
            'type': 'unknown',
            'validation': 'error',
            'error': f'Input path does not exist: {input_path}',
            'path': str(input_path)
        }
    
    # Check if it's a file (not directory)
    if not input_path.is_file():
        return {
            'type': 'unknown',
            'validation': 'error',
            'error': f'Input path is not a file: {input_path}',
            'path': str(input_path)
        }
    
    # Check file extension
    if input_path.suffix.lower() != '.json':
        return {
            'type': 'unknown',
            'validation': 'error',
            'error': f'Input file must have .json extension: {input_path}',
            'path': str(input_path)
        }
    
    # Try to parse JSON to validate
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Analyze JSON structure
        structure_info = analyze_json_structure(json_data)
        
        return {
            'type': 'json',
            'validation': 'valid',
            'path': str(input_path),
            'size': input_path.stat().st_size,
            'structure': structure_info,
            'data': json_data
        }
        
    except json.JSONDecodeError as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Invalid JSON format: {str(e)}',
            'path': str(input_path)
        }
    except Exception as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Error reading file: {str(e)}',
            'path': str(input_path)
        }

def analyze_json_structure(data, max_depth=3, current_depth=0):
    """
    Analyze JSON structure to provide insights about the data
    
    Args:
        data: JSON data to analyze
        max_depth: Maximum depth to analyze
        current_depth: Current depth in recursion
        
    Returns:
        dict: Structure analysis information
    """
    if current_depth >= max_depth:
        return {'type': 'truncated', 'depth': current_depth}
    
    if isinstance(data, dict):
        return {
            'type': 'object',
            'keys': list(data.keys()),
            'key_count': len(data),
            'children': {
                key: analyze_json_structure(value, max_depth, current_depth + 1)
                for key, value in data.items()
            } if current_depth < max_depth - 1 else None
        }
    elif isinstance(data, list):
        return {
            'type': 'array',
            'length': len(data),
            'sample_items': [
                analyze_json_structure(item, max_depth, current_depth + 1)
                for item in data[:3]  # Sample first 3 items
            ] if data and current_depth < max_depth - 1 else None
        }
    else:
        return {
            'type': 'primitive',
            'value_type': type(data).__name__,
            'sample_value': str(data)[:100] if data is not None else None
        }

def validate_json_file(file_path):
    """
    Validate that a file contains valid JSON
    
    Args:
        file_path (str or Path): Path to JSON file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {str(e)}"
    except Exception as e:
        return False, f"File read error: {str(e)}"

def get_json_file_info(file_path):
    """
    Get detailed information about a JSON file
    
    Args:
        file_path (str or Path): Path to JSON file
        
    Returns:
        dict: File information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {'error': 'File does not exist'}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'file_size': file_path.stat().st_size,
            'encoding': 'utf-8',
            'structure': analyze_json_structure(data),
            'root_type': type(data).__name__,
            'is_valid': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'is_valid': False
        } 