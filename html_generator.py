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
        
        /* Context Menu */
        .context-menu {
            position: fixed;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 4px 0;
            z-index: 1000;
            display: none;
            min-width: 150px;
        }
        
        .context-menu-item {
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            color: #333;
        }
        
        .context-menu-item:hover {
            background-color: #f0f0f0;
        }
        
        .context-menu-separator {
            height: 1px;
            background-color: #e0e0e0;
            margin: 4px 0;
        }
        
        /* Notifications */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1001;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        }
        
        .notification.show {
            opacity: 1;
            transform: translateX(0);
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
        
        // TreeNode class for managing individual tree nodes
        class TreeNode {{
            constructor(data, path, type, parent = null) {{
                this.data = data;
                this.path = path;
                this.type = type;
                this.parent = parent;
                this.children = [];
                this.expanded = false;
                this.selected = false;
                this.element = null;
                this.depth = parent ? parent.depth + 1 : 0;
            }}
            
            addChild(child) {{
                child.parent = this;
                child.depth = this.depth + 1;
                this.children.push(child);
                return child;
            }}
            
            removeChild(child) {{
                const index = this.children.indexOf(child);
                if (index > -1) {{
                    this.children.splice(index, 1);
                    child.parent = null;
                }}
                return child;
            }}
            
            toggleExpanded() {{
                this.expanded = !this.expanded;
                if (this.element) {{
                    const children = this.element.querySelector('.tree-children');
                    const toggle = this.element.querySelector('.expand-toggle');
                    if (children && toggle) {{
                        if (this.expanded) {{
                            children.classList.add('expanded');
                            toggle.textContent = '▼';
                        }} else {{
                            children.classList.remove('expanded');
                            toggle.textContent = '▶';
                        }}
                    }}
                }}
                return this.expanded;
            }}
            
            select() {{
                // Deselect all other nodes
                TreeNode.deselectAll();
                this.selected = true;
                if (this.element) {{
                    this.element.classList.add('selected');
                }}
                return this;
            }}
            
            deselect() {{
                this.selected = false;
                if (this.element) {{
                    this.element.classList.remove('selected');
                }}
                return this;
            }}
            
            static deselectAll() {{
                document.querySelectorAll('.tree-node').forEach(node => {{
                    node.classList.remove('selected');
                }});
                TreeNode.selectedNodes.forEach(node => {{
                    node.selected = false;
                }});
                TreeNode.selectedNodes = [];
            }}
            
            static selectedNodes = [];
            
            static createFromData(data, path = '', parent = null) {{
                let type = 'primitive';
                if (Array.isArray(data)) {{
                    type = 'array';
                }} else if (data !== null && typeof data === 'object') {{
                    type = 'object';
                }}
                
                const node = new TreeNode(data, path, type, parent);
                
                if (type === 'object') {{
                    Object.keys(data).forEach(key => {{
                        const childPath = path ? `${{path}}.${{key}}` : key;
                        const childNode = TreeNode.createFromData(data[key], childPath, node);
                        node.addChild(childNode);
                    }});
                }} else if (type === 'array') {{
                    data.forEach((item, index) => {{
                        const childPath = `${{path}}[${{index}}]`;
                        const childNode = TreeNode.createFromData(item, childPath, node);
                        node.addChild(childNode);
                    }});
                }}
                
                return node;
            }}
            
            findNodeByPath(targetPath) {{
                if (this.path === targetPath) {{
                    return this;
                }}
                
                for (const child of this.children) {{
                    const found = child.findNodeByPath(targetPath);
                    if (found) return found;
                }}
                
                return null;
            }}
            
            expandToPath(targetPath) {{
                if (this.path === targetPath) {{
                    return true;
                }}
                
                for (const child of this.children) {{
                    if (child.path === targetPath || targetPath.startsWith(child.path + '.')) {{
                        this.expanded = true;
                        if (this.element) {{
                            const children = this.element.querySelector('.tree-children');
                            const toggle = this.element.querySelector('.expand-toggle');
                            if (children && toggle) {{
                                children.classList.add('expanded');
                                toggle.textContent = '▼';
                            }}
                        }}
                        return child.expandToPath(targetPath);
                    }}
                }}
                
                return false;
            }}
            
            getValue() {{
                return this.data;
            }}
            
            getDisplayName() {{
                if (this.parent) {{
                    if (this.parent.type === 'array') {{
                        const index = this.parent.children.indexOf(this);
                        return `[${{index}}]`;
                    }} else {{
                        const parentPath = this.parent.path;
                        const fullPath = this.path;
                        return fullPath.substring(parentPath.length + 1);
                    }}
                }}
                return this.path || 'root';
            }}
            
            getType() {{
                return this.type;
            }}
            
            hasChildren() {{
                return this.children.length > 0;
            }}
            
            getChildCount() {{
                return this.children.length;
            }}
        }}
        
        // ContentRenderer class for displaying JSON content
        class ContentRenderer {{
            constructor() {{
                this.contentView = null;
                this.currentNode = null;
                this.config = {{
                    showLineNumbers: true,
                    enableSyntaxHighlighting: true,
                    maxDisplayLength: 1000,
                    expandLevels: 2
                }};
            }}
            
            initialize(contentViewElement) {{
                this.contentView = contentViewElement;
                return this;
            }}
            
            render(node) {{
                if (!this.contentView) {{
                    console.error('ContentRenderer not initialized');
                    return;
                }}
                
                this.currentNode = node;
                const html = this.generateHTML(node);
                this.contentView.innerHTML = html;
                
                // Update path display
                this.updatePathDisplay(node.path);
                
                return this;
            }}
            
            generateHTML(node) {{
                if (!node) {{
                    return '<div class="error">No node selected</div>';
                }}
                
                const data = node.getValue();
                const type = node.getType();
                
                switch (type) {{
                    case 'object':
                        return this.renderObject(data, node);
                    case 'array':
                        return this.renderArray(data, node);
                    case 'primitive':
                        return this.renderPrimitive(data);
                    default:
                        return '<div class="error">Unknown data type</div>';
                }}
            }}
            
            renderObject(obj, node) {{
                if (!obj || typeof obj !== 'object') {{
                    return '<div class="json-object">{{}}</div>';
                }}
                
                const keys = Object.keys(obj);
                if (keys.length === 0) {{
                    return '<div class="json-object">{{}}</div>';
                }}
                
                let html = '<div class="json-object">';
                html += '<div class="json-object-header">Object with ' + keys.length + ' properties</div>';
                
                keys.forEach(key => {{
                    const value = obj[key];
                    const valueType = this.getTypeName(value);
                    const displayValue = this.formatValue(value, 0);
                    
                    html += `<div class="json-property">`;
                    html += `<span class="json-key">"${{key}}"</span>: `;
                    html += `<span class="json-value ${{valueType}}-value">${{displayValue}}</span>`;
                    html += `</div>`;
                }});
                
                html += '</div>';
                return html;
            }}
            
            renderArray(arr, node) {{
                if (!Array.isArray(arr)) {{
                    return '<div class="json-array">[]</div>';
                }}
                
                if (arr.length === 0) {{
                    return '<div class="json-array">[]</div>';
                }}
                
                let html = '<div class="json-array">';
                html += '<div class="json-array-header">Array with ' + arr.length + ' items</div>';
                
                arr.forEach((item, index) => {{
                    const valueType = this.getTypeName(item);
                    const displayValue = this.formatValue(item, 0);
                    
                    html += `<div class="json-array-item">`;
                    html += `<span class="json-index">[${{index}}]</span>: `;
                    html += `<span class="json-value ${{valueType}}-value">${{displayValue}}</span>`;
                    html += `</div>`;
                }});
                
                html += '</div>';
                return html;
            }}
            
            renderPrimitive(value) {{
                const type = this.getTypeName(value);
                const displayValue = this.formatValue(value, 0);
                
                return `<div class="json-primitive">
                    <span class="json-value ${{type}}-value">${{displayValue}}</span>
                    <div class="json-type-info">Type: ${{type}}</div>
                </div>`;
            }}
            
            formatValue(value, level = 0) {{
                if (level > this.config.expandLevels) {{
                    return this.getTypeName(value) + '...';
                }}
                
                if (value === null) {{
                    return '<span class="json-null">null</span>';
                }}
                
                if (typeof value === 'boolean') {{
                    return `<span class="json-boolean">${{value}}</span>`;
                }}
                
                if (typeof value === 'number') {{
                    return `<span class="json-number">${{value}}</span>`;
                }}
                
                if (typeof value === 'string') {{
                    const truncated = value.length > this.config.maxDisplayLength 
                        ? value.substring(0, this.config.maxDisplayLength) + '...'
                        : value;
                    return `<span class="json-string">"${{truncated}}"</span>`;
                }}
                
                if (Array.isArray(value)) {{
                    if (level >= this.config.expandLevels) {{
                        return `<span class="json-array">[Array with ${{value.length}} items]</span>`;
                    }}
                    
                    let html = '<span class="json-array">[';
                    const items = value.slice(0, 5); // Show first 5 items
                    items.forEach((item, index) => {{
                        if (index > 0) html += ', ';
                        html += this.formatValue(item, level + 1);
                    }});
                    if (value.length > 5) {{
                        html += `, ... (+${{value.length - 5}} more)`;
                    }}
                    html += ']</span>';
                    return html;
                }}
                
                if (typeof value === 'object') {{
                    if (level >= this.config.expandLevels) {{
                        const keys = Object.keys(value);
                        return `<span class="json-object">{{Object with ${{keys.length}} properties}}</span>`;
                    }}
                    
                    let html = '<span class="json-object">{{';
                    const keys = Object.keys(value).slice(0, 3); // Show first 3 properties
                    keys.forEach((key, index) => {{
                        if (index > 0) html += ', ';
                        html += `"${{key}}": ${{this.formatValue(value[key], level + 1)}}`;
                    }});
                    if (Object.keys(value).length > 3) {{
                        html += `, ... (+${{Object.keys(value).length - 3}} more)`;
                    }}
                    html += '}}</span>';
                    return html;
                }}
                
                return `<span class="json-unknown">${{value}}</span>`;
            }}
            
            getTypeName(value) {{
                if (value === null) return 'null';
                if (typeof value === 'boolean') return 'boolean';
                if (typeof value === 'number') return 'number';
                if (typeof value === 'string') return 'string';
                if (Array.isArray(value)) return 'array';
                if (typeof value === 'object') return 'object';
                return 'unknown';
            }}
            
            updatePathDisplay(path) {{
                const pathElement = document.getElementById('current-path');
                if (pathElement) {{
                    pathElement.textContent = path || 'root';
                }}
            }}
            
            setConfig(newConfig) {{
                this.config = {{...this.config, ...newConfig}};
                return this;
            }}
            
            getConfig() {{
                return {{...this.config}};
            }}
            
            clear() {{
                if (this.contentView) {{
                    this.contentView.innerHTML = '';
                }}
                this.currentNode = null;
                return this;
            }}
        }}
        
        // Event Handling System
        class EventHandler {{
            constructor() {{
                this.rootNode = null;
                this.contentRenderer = null;
                this.selectedNode = null;
                this.contextMenu = null;
                this.isInitialized = false;
            }}
            
            initialize(rootNode, contentRenderer) {{
                this.rootNode = rootNode;
                this.contentRenderer = contentRenderer;
                this.setupEventListeners();
                this.createContextMenu();
                this.isInitialized = true;
                return this;
            }}
            
            setupEventListeners() {{
                // Tree node click events
                document.addEventListener('click', (e) => this.handleNodeClick(e));
                document.addEventListener('dblclick', (e) => this.handleNodeDoubleClick(e));
                document.addEventListener('contextmenu', (e) => this.handleContextMenu(e));
                
                // Keyboard events
                document.addEventListener('keydown', (e) => this.handleKeyboard(e));
                
                // Global click to close context menu
                document.addEventListener('click', (e) => this.closeContextMenu(e));
                
                // Expand/collapse all buttons
                this.setupToolbarEvents();
            }}
            
            handleNodeClick(e) {{
                const treeNode = e.target.closest('.tree-node');
                if (!treeNode) return;
                
                const expandToggle = e.target.closest('.expand-toggle');
                if (expandToggle) {{
                    this.toggleNodeExpansion(treeNode);
                    return;
                }}
                
                this.selectNode(treeNode);
            }}
            
            handleNodeDoubleClick(e) {{
                const treeNode = e.target.closest('.tree-node');
                if (!treeNode) return;
                
                const expandToggle = e.target.closest('.expand-toggle');
                if (expandToggle) return; // Don't double-expand toggle buttons
                
                this.toggleNodeExpansion(treeNode);
            }}
            
            handleContextMenu(e) {{
                const treeNode = e.target.closest('.tree-node');
                if (!treeNode) return;
                
                e.preventDefault();
                this.showContextMenu(e, treeNode);
            }}
            
            handleKeyboard(e) {{
                if (!this.selectedNode) return;
                
                switch (e.key) {{
                    case 'ArrowUp':
                        e.preventDefault();
                        this.selectPreviousNode();
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        this.selectNextNode();
                        break;
                    case 'ArrowLeft':
                        e.preventDefault();
                        this.collapseSelectedNode();
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        this.expandSelectedNode();
                        break;
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        this.toggleSelectedNodeExpansion();
                        break;
                    case 'Escape':
                        this.closeContextMenu();
                        break;
                }}
            }}
            
            selectNode(treeNode) {{
                // Remove previous selection
                if (this.selectedNode) {{
                    this.selectedNode.classList.remove('selected');
                }}
                
                // Add selection to current node
                treeNode.classList.add('selected');
                this.selectedNode = treeNode;
                
                // Update content
                const nodePath = treeNode.getAttribute('data-path');
                const node = this.rootNode.findNodeByPath(nodePath);
                if (node && this.contentRenderer) {{
                    this.contentRenderer.render(node);
                }}
            }}
            
            toggleNodeExpansion(treeNode) {{
                const nodePath = treeNode.getAttribute('data-path');
                const node = this.rootNode.findNodeByPath(nodePath);
                
                if (node) {{
                    node.toggleExpanded();
                }}
            }}
            
            selectPreviousNode() {{
                if (!this.selectedNode) return;
                
                const prevNode = this.selectedNode.previousElementSibling;
                if (prevNode && prevNode.classList.contains('tree-node')) {{
                    this.selectNode(prevNode);
                    this.scrollToNode(prevNode);
                }}
            }}
            
            selectNextNode() {{
                if (!this.selectedNode) return;
                
                const nextNode = this.selectedNode.nextElementSibling;
                if (nextNode && nextNode.classList.contains('tree-node')) {{
                    this.selectNode(nextNode);
                    this.scrollToNode(nextNode);
                }}
            }}
            
            expandSelectedNode() {{
                if (!this.selectedNode) return;
                
                const nodePath = this.selectedNode.getAttribute('data-path');
                const node = this.rootNode.findNodeByPath(nodePath);
                
                if (node && !node.expanded) {{
                    node.toggleExpanded();
                }}
            }}
            
            collapseSelectedNode() {{
                if (!this.selectedNode) return;
                
                const nodePath = this.selectedNode.getAttribute('data-path');
                const node = this.rootNode.findNodeByPath(nodePath);
                
                if (node && node.expanded) {{
                    node.toggleExpanded();
                }}
            }}
            
            toggleSelectedNodeExpansion() {{
                if (!this.selectedNode) return;
                
                const nodePath = this.selectedNode.getAttribute('data-path');
                const node = this.rootNode.findNodeByPath(nodePath);
                
                if (node) {{
                    node.toggleExpanded();
                }}
            }}
            
            scrollToNode(node) {{
                node.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
            
            createContextMenu() {{
                this.contextMenu = document.createElement('div');
                this.contextMenu.className = 'context-menu';
                this.contextMenu.innerHTML = `
                    <div class="context-menu-item" data-action="expand">Expand</div>
                    <div class="context-menu-item" data-action="collapse">Collapse</div>
                    <div class="context-menu-separator"></div>
                    <div class="context-menu-item" data-action="expand-all">Expand All Children</div>
                    <div class="context-menu-item" data-action="collapse-all">Collapse All Children</div>
                    <div class="context-menu-separator"></div>
                    <div class="context-menu-item" data-action="copy-path">Copy Path</div>
                    <div class="context-menu-item" data-action="copy-value">Copy Value</div>
                `;
                
                document.body.appendChild(this.contextMenu);
                
                // Add event listeners to context menu items
                this.contextMenu.addEventListener('click', (e) => this.handleContextMenuAction(e));
            }}
            
            showContextMenu(e, treeNode) {{
                this.contextMenu.style.display = 'block';
                this.contextMenu.style.left = e.pageX + 'px';
                this.contextMenu.style.top = e.pageY + 'px';
                
                // Store reference to the target node
                this.contextMenu.setAttribute('data-target-node', treeNode.getAttribute('data-path'));
            }}
            
            closeContextMenu(e) {{
                if (this.contextMenu && (!e || !this.contextMenu.contains(e.target))) {{
                    this.contextMenu.style.display = 'none';
                }}
            }}
            
            handleContextMenuAction(e) {{
                const menuItem = e.target.closest('.context-menu-item');
                if (!menuItem) return;
                
                const action = menuItem.getAttribute('data-action');
                const targetPath = this.contextMenu.getAttribute('data-target-node');
                const node = this.rootNode.findNodeByPath(targetPath);
                
                if (!node) return;
                
                switch (action) {{
                    case 'expand':
                        if (!node.expanded) node.toggleExpanded();
                        break;
                    case 'collapse':
                        if (node.expanded) node.toggleExpanded();
                        break;
                    case 'expand-all':
                        this.expandAllChildren(node);
                        break;
                    case 'collapse-all':
                        this.collapseAllChildren(node);
                        break;
                    case 'copy-path':
                        this.copyToClipboard(node.path);
                        break;
                    case 'copy-value':
                        this.copyToClipboard(JSON.stringify(node.getValue(), null, 2));
                        break;
                }}
                
                this.closeContextMenu();
            }}
            
            expandAllChildren(node) {{
                node.expanded = true;
                if (node.element) {{
                    const children = node.element.querySelector('.tree-children');
                    const toggle = node.element.querySelector('.expand-toggle');
                    if (children && toggle) {{
                        children.classList.add('expanded');
                        toggle.textContent = '▼';
                    }}
                }}
                
                node.children.forEach(child => this.expandAllChildren(child));
            }}
            
            collapseAllChildren(node) {{
                node.expanded = false;
                if (node.element) {{
                    const children = node.element.querySelector('.tree-children');
                    const toggle = node.element.querySelector('.expand-toggle');
                    if (children && toggle) {{
                        children.classList.remove('expanded');
                        toggle.textContent = '▶';
                    }}
                }}
                
                node.children.forEach(child => this.collapseAllChildren(child));
            }}
            
            copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(() => {{
                    this.showNotification('Copied to clipboard!');
                }}).catch(() => {{
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    this.showNotification('Copied to clipboard!');
                }});
            }}
            
            showNotification(message) {{
                const notification = document.createElement('div');
                notification.className = 'notification';
                notification.textContent = message;
                document.body.appendChild(notification);
                
                setTimeout(() => {{
                    notification.classList.add('show');
                }}, 100);
                
                setTimeout(() => {{
                    notification.classList.remove('show');
                    setTimeout(() => {{
                        document.body.removeChild(notification);
                    }}, 300);
                }}, 2000);
            }}
            
            setupToolbarEvents() {{
                // Expand all button
                const expandAllBtn = document.getElementById('expand-all-btn');
                if (expandAllBtn) {{
                    expandAllBtn.addEventListener('click', () => {{
                        this.expandAllChildren(this.rootNode);
                    }});
                }}
                
                // Collapse all button
                const collapseAllBtn = document.getElementById('collapse-all-btn');
                if (collapseAllBtn) {{
                    collapseAllBtn.addEventListener('click', () => {{
                        this.collapseAllChildren(this.rootNode);
                    }});
                }}
            }}
        }}
        
        // Current selected node and root node
        let selectedNode = null;
        let rootNode = null;
        let contentRenderer = null;
        let eventHandler = null;
        
        // Initialize the explorer
        document.addEventListener('DOMContentLoaded', function() {{
            initializeExplorer();
        }});
        
        function initializeExplorer() {{
            // Create tree structure from JSON data
            rootNode = TreeNode.createFromData(jsonData);
            
            // Initialize content renderer
            const contentView = document.getElementById('content-view');
            contentRenderer = new ContentRenderer().initialize(contentView);
            
            // Initialize event handler
            eventHandler = new EventHandler().initialize(rootNode, contentRenderer);
            
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
            
            // Update content using ContentRenderer
            const node = rootNode.findNodeByPath(path);
            if (node && contentRenderer) {{
                contentRenderer.render(node);
            }}
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