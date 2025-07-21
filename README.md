# JSON to HTML Explorer Tool

A powerful tool that converts JSON files into interactive HTML explorers with a Windows Explorer-like interface. Navigate through complex JSON structures with ease using an intuitive tree view and content viewer.

## 🚀 Features

- **Interactive Tree View**: Navigate JSON structure with expandable/collapsible nodes
- **Content Viewer**: View detailed JSON content with syntax highlighting
- **Windows Explorer-like Interface**: Familiar two-pane layout
- **File Validation**: Comprehensive JSON validation with detailed error messages
- **Error Handling**: Robust error handling with actionable guidance
- **Responsive Design**: Clean, modern interface that works on different screen sizes
- **Batch Processing**: Process multiple JSON files with timestamped outputs

## 📋 Requirements

- Python 3.7+
- loguru (for logging)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/rubenxyz/json->html_tool.git
cd json->html_tool
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Basic Usage

Convert a JSON file to HTML:
```bash
python json_to_html.py input/sample.json
```

### Advanced Usage

Specify custom output path:
```bash
python json_to_html.py input/sample.json output/custom_name.html
```

### Input/Output Structure

The tool follows a simple workflow:
- **Input**: JSON files placed in the `input/` directory
- **Output**: HTML files generated in timestamped folders under `output/`

Example output structure:
```
output/
├── 2025-07-21_07-31-40/
│   ├── sample.html
│   ├── conversion_log.json
│   └── conversion_summary.md
└── 2025-07-21_08-15-22/
    ├── another_file.html
    ├── conversion_log.json
    └── conversion_summary.md
```

## 🎨 Interface Features

### Tree View (Left Panel)
- **📁 Objects**: Expandable folders for JSON objects
- **📋 Arrays**: Expandable lists for JSON arrays  
- **📄 Primitives**: Individual values (strings, numbers, booleans, null)
- **Count Indicators**: Shows number of items in objects/arrays
- **Auto-expansion**: First two levels automatically expanded

### Content Viewer (Right Panel)
- **Syntax Highlighting**: Color-coded JSON values by type
- **Path Display**: Shows current node path
- **File Information**: Displays file name, size, and type
- **Formatted Display**: Clean, readable JSON presentation

### Navigation
- **Click to Select**: Click any node to view its content
- **Expand/Collapse**: Click arrow icons to expand/collapse nodes
- **Visual Feedback**: Selected nodes are highlighted

## 🔧 Configuration

The tool supports various configuration options:

```python
config = {
    'title': 'JSON Explorer',           # HTML page title
    'theme': 'light',                   # Theme (light/dark)
    'auto_expand_levels': 2,           # Auto-expand first N levels
    'show_line_numbers': True,         # Show line numbers in content
    'enable_syntax_highlighting': True # Enable syntax highlighting
}
```

## ⚠️ Error Handling

The tool provides comprehensive error handling for various scenarios:

### File Errors
- **File Not Found**: Clear path guidance
- **Permission Denied**: Permission troubleshooting
- **Empty Files**: Validation for empty JSON files
- **File Too Large**: Size limit enforcement (100MB max)
- **Invalid Extension**: Only .json files supported

### JSON Errors
- **Syntax Errors**: Line-specific error reporting
- **Encoding Issues**: UTF-8 encoding validation
- **Structure Problems**: Deep nesting and size validation
- **Invalid Types**: Unsupported data type detection

### Error Messages
Each error includes:
- Clear error description
- Error code for programmatic handling
- Actionable guidance for resolution
- Line numbers for syntax errors

## 📁 Project Structure

```
json->html_tool/
├── json_to_html.py          # Main entry point
├── input_detector.py        # JSON file validation
├── json_parser.py          # JSON parsing and analysis
├── html_generator.py       # HTML generation
├── requirements.txt        # Python dependencies
├── input/                  # Input JSON files
│   ├── sample.json
│   └── invalid.json
├── output/                 # Generated HTML files
└── .taskmaster/           # Project management
    ├── docs/
    │   └── prd.txt        # Product requirements
    └── tasks/
        └── tasks.json     # Development tasks
```

## 🧪 Testing

### Test Cases Included

1. **Valid JSON**: `input/sample.json` - Comprehensive test data
2. **Invalid JSON**: `input/invalid.json` - Error handling tests

### Running Tests

Test with valid JSON:
```bash
python json_to_html.py input/sample.json
```

Test error handling:
```bash
python json_to_html.py input/invalid.json
python json_to_html.py input/nonexistent.json
python json_to_html.py input_detector.py
```

## 🔍 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'loguru'"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Input file must have .json extension"**
- Ensure your file has a `.json` extension
- Only JSON files are supported

**"Invalid JSON format"**
- Check the JSON syntax using a JSON validator
- Look for missing quotes, commas, or brackets
- Ensure proper UTF-8 encoding

**"File is too large"**
- Split large JSON files into smaller chunks
- Maximum file size is 100MB

### Getting Help

1. Check the conversion logs in the output directory
2. Review the error messages for specific guidance
3. Ensure your JSON file is valid using online validators
4. Check file permissions and encoding

## 🚀 Development

### Architecture

The tool follows a modular architecture:

1. **Input Detection** (`input_detector.py`): Validates and analyzes JSON files
2. **JSON Parsing** (`json_parser.py`): Parses JSON and prepares tree structure
3. **HTML Generation** (`html_generator.py`): Creates interactive HTML interface
4. **Main Orchestration** (`json_to_html.py`): Coordinates the entire process

### Adding Features

To extend the tool:

1. **New Validation Rules**: Add to `validate_json_structure()` in `input_detector.py`
2. **UI Enhancements**: Modify CSS and JavaScript in `html_generator.py`
3. **New Output Formats**: Extend `html_generator.py` with new generators
4. **Configuration Options**: Add to the config dictionary in `json_to_html.py`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the error logs in the output directory

---

**Happy JSON Exploring! 🎉** 