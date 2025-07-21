#!/usr/bin/env python3
"""
Markdown/XML to JSON Converter
Converts markdown folders or XML files to JSON output optimized for LLM parsing
"""

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Import our modules
from input_detector import get_input_info
from parser import parse_markdown_folder, parse_xml_file
from json_generator import write_json_file, create_llm_optimized_json

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

def convert_to_json(input_path, output_path=None, config=None):
    """
    Convert markdown folder or XML file to JSON
    
    Args:
        input_path (str or Path): Path to input (folder or XML file)
        output_path (str or Path, optional): Output JSON file path
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
        
        # Parse input based on type
        if input_info['type'] == 'markdown':
            logger.info("Parsing markdown folder...")
            internal_data = parse_markdown_folder(input_path, config)
        else:  # xml
            logger.info("Parsing XML file...")
            internal_data = parse_xml_file(input_path)
        
        # Generate output path if not provided
        if output_path is None:
            if input_info['type'] == 'markdown':
                input_path_obj = Path(input_path)
                # Check if we're pointing to a specific subfolder (not the input folder)
                if input_path_obj.name != 'input':
                    # Use the actual folder name
                    input_name = input_path_obj.name
                else:
                    # For the input folder, use the first subfolder name
                    subdirs = [d for d in input_path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    if subdirs:
                        # Use the first subfolder name as the JSON filename
                        input_name = subdirs[0].name
                    else:
                        # Fallback to input folder name if no subdirs
                        input_name = input_path_obj.name
            else:
                # For XML files, use the file stem
                input_name = Path(input_path).stem
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = f"output/{timestamp}/{input_name}.json"
        
        # Create LLM-optimized JSON
        logger.info("Generating LLM-optimized JSON...")
        llm_json = create_llm_optimized_json(internal_data, config)
        
        # Write JSON file
        success = write_json_file(llm_json, output_path, config)
        
        if success:
            logger.info(f"✅ Conversion successful!")
            logger.info(f"📁 Input: {input_path}")
            logger.info(f"📄 Output: {output_path}")
            logger.info(f"📊 Files processed: {len(internal_data.get('files', []))}")
            logger.info(f"📝 Total instructions: {llm_json['instructions']['total_instructions']}")
            return True
        else:
            logger.error("❌ Failed to write JSON file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        return False

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert markdown folders or XML files to JSON')
    parser.add_argument('input', help='Input path (markdown folder or XML file)')
    parser.add_argument('-o', '--output', help='Output JSON file path')
    parser.add_argument('--indent', type=int, default=2, help='JSON indentation (default: 2)')
    parser.add_argument('--sort-keys', action='store_true', help='Sort JSON keys')
    parser.add_argument('--ensure-ascii', action='store_true', help='Ensure ASCII output')
    
    args = parser.parse_args()
    
    # Setup configuration
    config = {
        'indent': args.indent,
        'sort_keys': args.sort_keys,
        'ensure_ascii': args.ensure_ascii
    }
    
    # Create output directory for logging
    if args.output:
        output_dir = Path(args.output).parent
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = Path(f"output/{timestamp}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(output_dir)
    
    logger.info("🚀 Starting Markdown/XML to JSON conversion")
    
    # Perform conversion
    success = convert_to_json(args.input, args.output, config)
    
    if success:
        logger.info("🎉 Conversion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 