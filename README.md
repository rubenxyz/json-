# Markdown/XML to JSON Converter

A flexible Python tool that converts markdown folders or XML files to JSON output optimized for LLM parsing. The tool automatically detects input type, preserves folder structure, and generates LLM-friendly JSON with hierarchical organization.

## Features

- **Dual Input Support**: Markdown folders OR XML files
- **JSON Output**: LLM-optimized JSON format
- **Automatic Detection**: Detects input type automatically
- **Header-Based Parsing**: Uses markdown headers (H1, H2, H3, etc.) to determine structure
- **Folder Structure Preservation**: Maintains complete folder hierarchy in JSON
- **Smart Filenames**: JSON files named after actual content folders
- **Timestamped Output**: Creates timestamped output directories
- **Comprehensive Logging**: Detailed logs and processing summaries
- **Unit Testing**: Includes comprehensive test suite

## Installation

1. **Clone or download** the script files to your project directory
2. **Install dependencies**:
   ```bash
   pip install loguru
   ```
   Or use the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

**Convert Markdown Folder:**
```bash
python markdown_xml_to_json.py input/folder_name
```

**Convert XML File:**
```bash
python markdown_xml_to_json.py input/document.xml
```

**Convert Entire Input Directory:**
```bash
python markdown_xml_to_json.py input
```

**Specify Output File:**
```bash
python markdown_xml_to_json.py input/folder_name -o output/custom_name.json
```

### Input Structure

**Markdown Folders:**
```
input/
├── Fal Documentation/
│   ├── 01. fal/
│   │   ├── 01.1 Introduction.md
│   │   └── 01.2 Quickstart.md
│   └── 02. Models/
│       ├── model1.md
│       └── model2.md
```

**XML Files:**
```
input/
└── document.xml
```

### Output Structure

```
output/
└── 2025-07-20_20-39-46/
    ├── Fal Documentation.json
    ├── conversion_log.json
    └── conversion_summary.md
```

### Input Structure

The script automatically detects your folder structure:

- **Folder Names**: Used as documentation names in XML output
- **File Names**: Preserved in XML with unique IDs
- **Header Structure**: Determines XML hierarchy

### Markdown Header Structure

The script uses markdown headers to create XML hierarchy:

```markdown
# H1 - Top Level Section
Content for H1 section

## H2 - Main Section
Content for H2 section

### H3 - Subsection
Content for H3 section

#### H4 - Sub-subsection
Content for H4 section

##### H5 - Deep subsection
Content for H5 section

###### H6 - Deepest subsection
Content for H6 section
```

### XML Output Structure

Each folder generates a separate XML file with this structure:

```xml
<?xml version="1.0" ?>
<documentation name="folder-name" version="1.0" processed_at="2025-01-20_14-30-25" source_folder="folder-name">
  <folder id="01" name="folder-name">
    <file id="01.01" name="file1.md" path="input/folder1/file1.md">
      <section id="1.1" title="Introduction" level="2">
        <content>This is the introduction content.</content>
        <subsection id="1.1.1" title="Prerequisites" level="3">
          <content>Install Python 3.7+.</content>
        </subsection>
      </section>
    </file>
  </folder>
</documentation>
```

## Configuration

### Auto-Generated Configuration

The script automatically generates configuration from your folder structure:

- **Documentation Name**: Uses folder name
- **Version**: Set to "1.0"
- **Folder IDs**: Automatically assigned based on alphabetical order

### Manual Configuration (Optional)

You can create a `config.json` file in the input directory to override defaults:

```json
{
  "documentation_name": "Custom Documentation Name",
  "version": "2.0",
  "folders": {
    "folder1": "01",
    "folder2": "02",
    "another-folder": "03"
  }
}
```

## Output Files

### XML Files
- **`{folder-name}.xml`**: XML output for each input folder
- **`processing_log.xml`**: Detailed machine-readable log

### Summary Files
- **`processing_summary.md`**: Human-readable summary with statistics

## Error Handling

The script includes comprehensive error handling:

- **File Reading Errors**: Graceful handling of encoding and permission issues
- **XML Generation Errors**: Validation and error reporting
- **Configuration Errors**: Fallback to auto-generated configuration
- **Logging**: Detailed logs for debugging

## Examples

### Example 1: Simple Documentation

**Input Structure:**
```
input/
└── getting-started/
    ├── introduction.md
    └── installation.md
```

**Markdown Content (introduction.md):**
```markdown
# Getting Started

Welcome to our documentation.

## Introduction

This guide will help you get started.

### Prerequisites

- Python 3.7+
- Basic knowledge of markdown
```

**Generated XML:**
```xml
<documentation name="getting-started" version="1.0">
  <folder id="01" name="getting-started">
    <file id="01.01" name="introduction.md">
      <section id="" title="Getting Started" level="2">
        <content>Welcome to our documentation.</content>
        <subsection id="" title="Introduction" level="3">
          <content>This guide will help you get started.</content>
          <subsubsection id="" title="Prerequisites" level="4">
            <content>- Python 3.7+</content>
          </subsubsection>
        </subsection>
      </section>
    </file>
  </folder>
</documentation>
```

## Troubleshooting

### Common Issues

1. **No output generated**: Check that input directory exists and contains markdown files
2. **Encoding errors**: Ensure markdown files are UTF-8 encoded
3. **Permission errors**: Check file and directory permissions
4. **Empty XML files**: Verify markdown files contain headers

### Debugging

- Check `processing_log.xml` for detailed error information
- Review `processing_summary.md` for processing statistics
- Enable debug logging by modifying the log level in `main.py`

## Development

### Project Structure
```
markdown_to_xml_tool/
├── main.py              # Main orchestration script
├── parser.py            # Markdown parsing and text cleaning
├── xml_generator.py     # XML generation and file processing
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── tests/              # Unit tests
│   ├── __init__.py
│   └── test_basic.py
├── input/              # Input directory (create your folders here)
└── output/             # Output directory (auto-generated)
```

### Running Tests
```bash
python -m unittest tests.test_basic -v
```

## License

This project is open source and available under the MIT License. 