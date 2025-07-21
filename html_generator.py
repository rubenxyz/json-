#!/usr/bin/env python3
"""
HTML Generator for JSON to HTML Explorer Tool
Generates interactive HTML explorer with Windows Explorer-like interface
"""

import json
from pathlib import Path
from loguru import logger
from json_parser import prepare_tree_data, get_node_by_path, format_value_for_display

def create_interactive_html(json_data, config=None):
    """
    Create interactive HTML explorer for JSON data
    
    Args:
        json_data (dict): Parsed JSON data from json_parser
        config (dict, optional): Configuration options
        
    Returns:
        str: Complete HTML content
    """
    if config is None:
        config = {}
    
    # Extract data and metadata
    data = json_data['data']
    metadata = json_data['metadata']
    
    # Prepare tree data for JavaScript
    tree_data = prepare_tree_data(data)
    
    # Generate HTML
    html_content = generate_html_template(
        tree_data=tree_data,
        metadata=metadata,
        config=config
    )
    
    logger.info("Interactive HTML explorer generated successfully")
    return html_content

def generate_html_template(tree_data, metadata, config):
    """
    Generate the complete HTML template
    
    Args:
        tree_data (dict): Tree structure data
        metadata (dict): File metadata
        config (dict): Configuration options
        
    Returns:
        str: Complete HTML content
    """
    title = config.get('title', 'JSON Explorer')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{title}</h1>
            <div class="file-info">
                <span class="file-name">{metadata['file_name']}</span>
                <span class="file-size">({format_file_size(metadata['file_size'])})</span>
                <span class="file-type">{metadata['root_type']}</span>
            </div>
        </header>
        
        <main class="main-content">
            <aside class="tree-panel">
                <div class="tree-header">
                    <h3>Structure</h3>
                </div>
                <div class="tree-container">
                    <div id="tree-view" class="tree-view">
                        {generate_tree_html(tree_data)}
                    </div>
                </div>
            </aside>
            
            <section class="content-panel">
                <div class="content-header">
                    <h3>Content</h3>
                    <div class="path-display">
                        <span id="current-path">root</span>
                    </div>
                </div>
                <div class="content-container">
                    <div id="content-view" class="content-view">
                        {generate_content_html(tree_data)}
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <script>
        {generate_javascript(tree_data)}
    </script>
</body>
</html>"""
    
    return html

def generate_css():
    """Generate CSS styles for the explorer"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #2c3e50;
            color: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid #34495e;
        }
        
        .header h1 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        .file-info {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .file-name {
            font-weight: bold;
        }
        
        .file-size {
            margin-left: 0.5rem;
        }
        
        .file-type {
            margin-left: 0.5rem;
            background: #3498db;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        .tree-panel {
            width: 300px;
            background: white;
            border-right: 1px solid #ddd;
            display: flex;
            flex-direction: column;
        }
        
        .tree-header {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            background: #f8f9fa;
        }
        
        .tree-header h3 {
            font-size: 1rem;
            color: #495057;
        }
        
        .tree-container {
            flex: 1;
            overflow-y: auto;
        }
        
        .tree-view {
            padding: 0.5rem;
        }
        
        .tree-node {
            margin: 0.2rem 0;
        }
        
        .tree-node-content {
            display: flex;
            align-items: center;
            padding: 0.3rem 0.5rem;
            border-radius: 3px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .tree-node-content:hover {
            background-color: #f8f9fa;
        }
        
        .tree-node-content.selected {
            background-color: #e3f2fd;
            border-left: 3px solid #2196f3;
        }
        
        .tree-node-icon {
            margin-right: 0.5rem;
            font-size: 1.1rem;
            width: 1.2rem;
            text-align: center;
        }
        
        .tree-node-name {
            flex: 1;
            font-size: 0.9rem;
        }
        
        .tree-node-count {
            font-size: 0.8rem;
            color: #6c757d;
            margin-left: 0.5rem;
        }
        
        .tree-children {
            margin-left: 1.5rem;
            display: none;
        }
        
        .tree-children.expanded {
            display: block;
        }
        
        .content-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
        }
        
        .content-header {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .content-header h3 {
            font-size: 1rem;
            color: #495057;
        }
        
        .path-display {
            font-family: monospace;
            font-size: 0.9rem;
            color: #6c757d;
            background: #e9ecef;
            padding: 0.3rem 0.6rem;
            border-radius: 3px;
        }
        
        .content-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }
        
        .content-view {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .json-object {
            margin: 0.5rem 0;
        }
        
        .json-key {
            color: #d73a49;
            font-weight: bold;
        }
        
        .json-value {
            margin-left: 0.5rem;
        }
        
        .json-string {
            color: #032f62;
        }
        
        .json-number {
            color: #005cc5;
        }
        
        .json-boolean {
            color: #e36209;
        }
        
        .json-null {
            color: #6a737d;
        }
        
        .json-array {
            margin: 0.5rem 0;
        }
        
        .json-array-item {
            margin: 0.2rem 0;
            padding-left: 1rem;
        }
        
        .expand-toggle {
            cursor: pointer;
            margin-right: 0.3rem;
            font-size: 0.8rem;
            color: #6c757d;
            transition: transform 0.2s;
        }
        
        .expand-toggle.expanded {
            transform: rotate(90deg);
        }
    """

def generate_tree_html(node, level=0):
    """Generate HTML for tree view"""
    indent = "  " * level
    
    if node['type'] == 'truncated':
        return f'{indent}<div class="tree-node">...</div>'
    
    icon_map = {
        'object': '📁',
        'array': '📋',
        'primitive': '📄'
    }
    
    icon = icon_map.get(node['type'], '📄')
    expanded_class = 'expanded' if node.get('expanded', False) else ''
    
    # Generate count display
    count_display = ""
    if node['type'] == 'object' and node.get('children'):
        count_display = f'<span class="tree-node-count">({len(node["children"])})</span>'
    elif node['type'] == 'array' and node.get('children'):
        count_display = f'<span class="tree-node-count">[{len(node["children"])}]</span>'
    
    # Generate expand toggle
    expand_toggle = ""
    if node.get('children'):
        expand_toggle = f'<span class="expand-toggle {expanded_class}">▶</span>'
    
    html = f'{indent}<div class="tree-node" data-path="{node["id"]}">'
    html += f'{indent}  <div class="tree-node-content" onclick="selectNode(\'{node["id"]}\')">'
    html += f'{indent}    {expand_toggle}'
    html += f'{indent}    <span class="tree-node-icon">{icon}</span>'
    html += f'{indent}    <span class="tree-node-name">{node["name"]}</span>'
    html += f'{indent}    {count_display}'
    html += f'{indent}  </div>'
    
    if node.get('children'):
        html += f'{indent}  <div class="tree-children {expanded_class}" onclick="event.stopPropagation()">'
        for child in node['children']:
            html += generate_tree_html(child, level + 1)
        html += f'{indent}  </div>'
    
    html += f'{indent}</div>'
    return html

def generate_content_html(node):
    """Generate initial content view"""
    return format_json_for_display(node)

def format_json_for_display(data, level=0):
    """Format JSON data for display"""
    indent = "  " * level
    
    if isinstance(data, dict):
        html = f'{indent}<div class="json-object">'
        for key, value in data.items():
            html += f'{indent}  <div>'
            html += f'{indent}    <span class="json-key">"{key}"</span>: '
            html += f'{indent}    <span class="json-value">{format_json_for_display(value, level + 1)}</span>'
            html += f'{indent}  </div>'
        html += f'{indent}</div>'
        return html
    elif isinstance(data, list):
        html = f'{indent}<div class="json-array">'
        for i, item in enumerate(data):
            html += f'{indent}  <div class="json-array-item">'
            html += f'{indent}    <span class="json-key">[{i}]</span>: '
            html += f'{indent}    <span class="json-value">{format_json_for_display(item, level + 1)}</span>'
            html += f'{indent}  </div>'
        html += f'{indent}</div>'
        return html
    else:
        return format_value_for_display(data)

def generate_javascript(tree_data):
    """Generate JavaScript for interactivity"""
    # Escape the JSON data for JavaScript
    json_data_escaped = json.dumps(tree_data).replace('"', '\\"')
    
    return f"""
        // Store the complete JSON data
        const jsonData = JSON.parse("{json_data_escaped}");
        
        // Current selected node
        let selectedNode = null;
        
        // Initialize the explorer
        document.addEventListener('DOMContentLoaded', function() {{
            initializeExplorer();
        }});
        
        function initializeExplorer() {{
            // Set up click handlers for expand/collapse
            document.querySelectorAll('.expand-toggle').forEach(toggle => {{
                toggle.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    const node = this.closest('.tree-node');
                    const children = node.querySelector('.tree-children');
                    const isExpanded = children.classList.contains('expanded');
                    
                    if (isExpanded) {{
                        children.classList.remove('expanded');
                        this.classList.remove('expanded');
                    }} else {{
                        children.classList.add('expanded');
                        this.classList.add('expanded');
                    }}
                }});
            }});
            
            // Select root node by default
            selectNode('root');
        }}
        
        function selectNode(path) {{
            // Remove previous selection
            if (selectedNode) {{
                selectedNode.classList.remove('selected');
            }}
            
            // Add selection to current node
            const nodeElement = document.querySelector(`[data-path="${{path}}"]`);
            if (nodeElement) {{
                const contentElement = nodeElement.querySelector('.tree-node-content');
                contentElement.classList.add('selected');
                selectedNode = contentElement;
            }}
            
            // Update path display
            document.getElementById('current-path').textContent = path;
            
            // Update content view
            updateContentView(path);
        }}
        
        function updateContentView(path) {{
            const contentView = document.getElementById('content-view');
            const nodeData = getNodeByPath(jsonData, path);
            
            if (nodeData) {{
                contentView.innerHTML = formatNodeForDisplay(nodeData);
            }} else {{
                contentView.innerHTML = '<div class="error">Node not found</div>';
            }}
        }}
        
        function getNodeByPath(data, path) {{
            if (path === 'root') return data;
            
            // Simple path resolution for demo
            const parts = path.split('.');
            let current = data;
            
            for (const part of parts) {{
                if (current && current.children) {{
                    current = current.children.find(child => child.id === part);
                }} else {{
                    return null;
                }}
            }}
            
            return current;
        }}
        
        function formatNodeForDisplay(node) {{
            if (!node) return '<div class="error">Node not found</div>';
            
            if (node.type === 'primitive') {{
                return `<div class="json-value">${{formatValue(node.value)}}</div>`;
            }} else if (node.type === 'object') {{
                return formatObjectForDisplay(node);
            }} else if (node.type === 'array') {{
                return formatArrayForDisplay(node);
            }} else {{
                return '<div class="error">Unknown node type</div>';
            }}
        }}
        
        function formatValue(value) {{
            if (value === null) return '<span class="json-null">null</span>';
            if (typeof value === 'boolean') return `<span class="json-boolean">${{value}}</span>`;
            if (typeof value === 'number') return `<span class="json-number">${{value}}</span>`;
            if (typeof value === 'string') return `<span class="json-string">"${{value}}"</span>`;
            return `<span class="json-unknown">${{value}}</span>`;
        }}
        
        function formatObjectForDisplay(node) {{
            if (!node.children) return '<div class="json-object">{{}}</div>';
            
            let html = '<div class="json-object">';
            node.children.forEach(child => {{
                html += `<div><span class="json-key">"${{child.name}}"</span>: ${{formatNodeForDisplay(child)}}</div>`;
            }});
            html += '</div>';
            return html;
        }}
        
        function formatArrayForDisplay(node) {{
            if (!node.children) return '<div class="json-array">[]</div>';
            
            let html = '<div class="json-array">';
            node.children.forEach((child, index) => {{
                html += `<div class="json-array-item"><span class="json-key">[${{index}}]</span>: ${{formatNodeForDisplay(child)}}</div>`;
            }});
            html += '</div>';
            return html;
        }}
    """

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def write_html_file(html_content, output_path, config=None):
    """
    Write HTML content to file
    
    Args:
        html_content (str): HTML content to write
        output_path (str or Path): Output file path
        config (dict, optional): Configuration options
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML file written successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing HTML file: {e}")
        return False 