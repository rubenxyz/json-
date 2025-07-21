#!/usr/bin/env python3
"""
JSON to HTML Explorer Tool
Converts JSON files to interactive HTML explorer with Windows Explorer-like interface
"""

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Import our modules
from input_detector import get_input_info
from json_parser import parse_json_file
from html_generator import write_html_file, create_interactive_html

def setup_logging(output_dir):
    """Setup logging for the conversion process"""
    # Remove default logger
    logger.remove()
    
    # JSON log file
    json_log_path = output_dir / "conversion_log.json"
    logger.add(json_log_path, format="{time} | {level} | {message}", 
               serialize=True, level="DEBUG")
    
    # Human-readable log
    md_log_path = output_dir / "conversion_summary.md"
    logger.add(md_log_path, format="{message}", level="INFO")
    
    # Console output
    logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")

def convert_to_html(input_path, output_path=None, config=None):
    """
    Convert JSON file to interactive HTML explorer
    
    Args:
        input_path (str or Path): Path to input JSON file
        output_path (str or Path, optional): Output HTML file path
        config (dict, optional): Configuration options
        
    Returns:
        bool: True if successful, False otherwise
    """
    if config is None:
        config = {}
    
    try:
        # Detect and validate input
        logger.info(f"Analyzing input: {input_path}")
        input_info = get_input_info(input_path)
        
        logger.info(f"Input type: {input_info['type']}")
        logger.info(f"Validation: {input_info['validation']}")
        
        # Parse JSON file
        logger.info("Parsing JSON file...")
        json_data = parse_json_file(input_path, config)
        
        # Generate output path if not provided
        if output_path is None:
            input_name = Path(input_path).stem
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = f"output/{timestamp}/{input_name}.html"
        
        # Create interactive HTML
        logger.info("Generating interactive HTML explorer...")
        html_content = create_interactive_html(json_data, config)
        
        # Write HTML file
        success = write_html_file(html_content, output_path, config)
        
        if success:
            logger.info(f"✅ Conversion successful!")
            logger.info(f"📁 Input: {input_path}")
            logger.info(f"📄 Output: {output_path}")
            logger.info(f"📊 JSON structure: {len(json_data)} root elements")
            return True
        else:
            logger.error("❌ Failed to write HTML file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Conversion failed: {str(e)}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python json_to_html.py <input_json_file> [output_html_file]")
        print("Example: python json_to_html.py input/data.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"output/{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    setup_logging(output_dir)
    
    logger.info("🚀 Starting JSON to HTML Explorer conversion...")
    
    # Configuration options
    config = {
        'title': 'JSON Explorer',
        'theme': 'light',
        'auto_expand_levels': 2,
        'show_line_numbers': True,
        'enable_syntax_highlighting': True
    }
    
    # Perform conversion
    success = convert_to_html(input_path, output_path, config)
    
    if success:
        logger.info("🎉 Conversion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 