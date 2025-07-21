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
            'path': str(input_path),
            'error_code': 'FILE_NOT_FOUND'
        }
    
    # Check if it's a file (not directory)
    if not input_path.is_file():
        return {
            'type': 'unknown',
            'validation': 'error',
            'error': f'Input path is not a file: {input_path}',
            'path': str(input_path),
            'error_code': 'NOT_A_FILE'
        }
    
    # Check file size
    file_size = input_path.stat().st_size
    if file_size == 0:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Input file is empty: {input_path}',
            'path': str(input_path),
            'error_code': 'EMPTY_FILE'
        }
    
    # Check file size limit (100MB)
    if file_size > 100 * 1024 * 1024:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Input file is too large ({format_file_size(file_size)}). Maximum size is 100MB.',
            'path': str(input_path),
            'error_code': 'FILE_TOO_LARGE'
        }
    
    # Check file extension
    if input_path.suffix.lower() != '.json':
        return {
            'type': 'unknown',
            'validation': 'error',
            'error': f'Input file must have .json extension: {input_path}',
            'path': str(input_path),
            'error_code': 'INVALID_EXTENSION'
        }
    
    # Try to parse JSON to validate
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Validate JSON structure
        validation_result = validate_json_structure(json_data)
        if not validation_result['is_valid']:
            return {
                'type': 'json',
                'validation': 'error',
                'error': validation_result['error'],
                'path': str(input_path),
                'error_code': 'INVALID_STRUCTURE'
            }
        
        # Analyze JSON structure
        structure_info = analyze_json_structure(json_data)
        
        return {
            'type': 'json',
            'validation': 'valid',
            'path': str(input_path),
            'size': file_size,
            'structure': structure_info,
            'data': json_data,
            'warnings': validation_result.get('warnings', [])
        }
        
    except json.JSONDecodeError as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Invalid JSON format: {str(e)}',
            'path': str(input_path),
            'error_code': 'JSON_DECODE_ERROR',
            'line': get_json_error_line(str(e))
        }
    except UnicodeDecodeError as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'File encoding error: {str(e)}. Please ensure the file is UTF-8 encoded.',
            'path': str(input_path),
            'error_code': 'ENCODING_ERROR'
        }
    except PermissionError as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Permission denied: {str(e)}',
            'path': str(input_path),
            'error_code': 'PERMISSION_ERROR'
        }
    except Exception as e:
        return {
            'type': 'json',
            'validation': 'error',
            'error': f'Unexpected error reading file: {str(e)}',
            'path': str(input_path),
            'error_code': 'UNEXPECTED_ERROR'
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

def validate_json_structure(data, max_depth=50, current_depth=0):
    """
    Validate JSON structure for potential issues
    
    Args:
        data: JSON data to validate
        max_depth: Maximum allowed nesting depth
        current_depth: Current depth in recursion
        
    Returns:
        dict: Validation result with is_valid, error, and warnings
    """
    warnings = []
    
    # Check for excessive nesting
    if current_depth > max_depth:
        return {
            'is_valid': False,
            'error': f'JSON structure is too deeply nested (max {max_depth} levels)',
            'warnings': warnings
        }
    
    if isinstance(data, dict):
        # Check for empty objects
        if not data:
            warnings.append('Empty object detected')
        
        # Check for very large objects
        if len(data) > 10000:
            warnings.append(f'Large object detected with {len(data)} keys')
        
        # Validate each key-value pair
        for key, value in data.items():
            # Check for invalid key types
            if not isinstance(key, str):
                return {
                    'is_valid': False,
                    'error': f'Invalid key type: {type(key).__name__}. Only string keys are allowed.',
                    'warnings': warnings
                }
            
            # Check for very long keys
            if len(key) > 1000:
                warnings.append(f'Very long key detected: {key[:50]}...')
            
            # Recursively validate values
            result = validate_json_structure(value, max_depth, current_depth + 1)
            if not result['is_valid']:
                return result
            warnings.extend(result.get('warnings', []))
            
    elif isinstance(data, list):
        # Check for empty arrays
        if not data:
            warnings.append('Empty array detected')
        
        # Check for very large arrays
        if len(data) > 100000:
            warnings.append(f'Large array detected with {len(data)} items')
        
        # Validate each item
        for i, item in enumerate(data):
            result = validate_json_structure(item, max_depth, current_depth + 1)
            if not result['is_valid']:
                return result
            warnings.extend(result.get('warnings', []))
            
    elif isinstance(data, str):
        # Check for very long strings
        if len(data) > 1000000:
            warnings.append(f'Very long string detected ({len(data)} characters)')
            
    elif isinstance(data, (int, float)):
        # Check for very large numbers
        if abs(data) > 1e15:
            warnings.append(f'Very large number detected: {data}')
            
    elif data is None:
        # null values are fine
        pass
        
    else:
        return {
            'is_valid': False,
            'error': f'Unsupported data type: {type(data).__name__}',
            'warnings': warnings
        }
    
    return {
        'is_valid': True,
        'warnings': warnings
    }

def get_json_error_line(error_message):
    """
    Extract line number from JSON decode error message
    
    Args:
        error_message (str): JSON decode error message
        
    Returns:
        int or None: Line number if found
    """
    import re
    match = re.search(r'line (\d+)', error_message)
    if match:
        return int(match.group(1))
    return None

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

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