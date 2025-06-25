"""Linear ANSI to HTML converter with comprehensive color support."""

import re
from terminal_mcp_server.ansi_colors import parse_sgr_params, format_css_style

class LinearAnsiToHtmlConverter:
    """Convert ANSI escape sequences to HTML with proper linear text flow."""
    
    def __init__(self):
        self.ansi_pattern = re.compile(r'\x1b\[([0-9;?]*)([a-zA-Z])')
        self.current_state = {
            'fg_color': None,
            'bg_color': None,
            'bold': False,
            'dim': False,
            'italic': False,
            'underline': False,
            'blink': False,
            'reverse': False,
            'strikethrough': False,
            'hidden': False
        }
    
    def reset_state(self):
        """Reset formatting state."""
        self.current_state = {k: False if k != 'fg_color' and k != 'bg_color' else None 
                             for k in self.current_state}
    
    def update_state(self, new_state):
        """Update current state with new formatting."""
        self.current_state.update(new_state)
    
    def get_current_css(self):
        """Get CSS for current state."""
        return format_css_style(self.current_state)
    
    def convert_to_html(self, text: str, title: str = "Terminal Output") -> str:
        """Convert ANSI text to HTML with linear processing."""
        self.reset_state()
        
        result = []
        current_css = ""
        i = 0
        
        while i < len(text):
            # Look for ANSI escape sequences
            match = self.ansi_pattern.match(text, i)
            if match:
                params_str, command = match.groups()
                
                # Handle SGR (color/formatting) sequences
                if command == 'm':
                    new_state = parse_sgr_params(params_str)
                    self.update_state(new_state)
                    
                    # Check if CSS changed
                    new_css = self.get_current_css()
                    if new_css != current_css:
                        # Close previous span
                        if current_css:
                            result.append('</span>')
                        
                        # Open new span
                        if new_css:
                            result.append(f'<span style="{new_css}">')
                        
                        current_css = new_css
                
                # Skip other escape sequences (cursor movement, etc.)
                i = match.end()
            else:
                # Regular character
                char = text[i]
                
                # HTML escape
                if char == '<':
                    result.append('&lt;')
                elif char == '>':
                    result.append('&gt;')
                elif char == '&':
                    result.append('&amp;')
                elif char == '"':
                    result.append('&quot;')
                elif char == "'":
                    result.append('&#39;')
                elif char == '\t':
                    result.append('    ')  # Convert tabs to 4 spaces
                else:
                    result.append(char)
                
                i += 1
        
        # Close final span
        if current_css:
            result.append('</span>')
        
        # Generate complete HTML
        html_content = ''.join(result)
        
        css = self.generate_css()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="terminal">
        <pre class="terminal-content">{html_content}</pre>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_css(self) -> str:
        """Generate CSS for terminal styling."""
        return """        body {
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
        }
        
        .terminal {
            background-color: #000000;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            max-width: 100%;
            overflow-x: auto;
        }
        
        .terminal-content {
            color: #C0C0C0;
            background-color: transparent;
            font-size: 14px;
            line-height: 1.2;
            margin: 0;
            white-space: pre;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        /* Scrollbar styling for webkit browsers */
        .terminal::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        .terminal::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        
        .terminal::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 6px;
        }
        
        .terminal::-webkit-scrollbar-thumb:hover {
            background: #777;
        }"""

def convert_ansi_to_html_linear(text: str, title: str = "Terminal Output") -> str:
    """Convert ANSI text to HTML with linear processing."""
    converter = LinearAnsiToHtmlConverter()
    return converter.convert_to_html(text, title)
