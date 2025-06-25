"""ANSI escape sequence to HTML converter for terminal output rendering."""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TerminalState:
    """Represents the current state of terminal formatting."""
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    blink: bool = False
    reverse: bool = False
    hidden: bool = False


class AnsiToHtmlConverter:
    """Converts ANSI escape sequences to HTML with proper styling."""
    
    # Standard 16 colors (0-15)
    STANDARD_COLORS = {
        0: '#000000',   # Black
        1: '#800000',   # Dark Red
        2: '#008000',   # Dark Green
        3: '#808000',   # Dark Yellow
        4: '#000080',   # Dark Blue
        5: '#800080',   # Dark Magenta
        6: '#008080',   # Dark Cyan
        7: '#C0C0C0',   # Light Gray
        8: '#808080',   # Dark Gray
        9: '#FF0000',   # Red
        10: '#00FF00',  # Green
        11: '#FFFF00',  # Yellow
        12: '#0000FF',  # Blue
        13: '#FF00FF',  # Magenta
        14: '#00FFFF',  # Cyan
        15: '#FFFFFF',  # White
    }
    
    # ANSI escape sequence patterns
    CSI_PATTERN = re.compile(r'\x1b\[([0-9;]*)([a-zA-Z])')
    OSC_PATTERN = re.compile(r'\x1b\]([0-9;]*);([^\x07\x1b]*)\x07')
    SIMPLE_ESCAPE_PATTERN = re.compile(r'\x1b([a-zA-Z])')
    
    def __init__(self):
        """Initialize the converter."""
        self.reset_state()
    
    def reset_state(self):
        """Reset the terminal state to defaults."""
        self.state = TerminalState()
        self.cursor_row = 0
        self.cursor_col = 0
        self.saved_cursor = (0, 0)
        self.screen_buffer = []
        self.max_cols = 80
        self.max_rows = 24
    
    def rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB values to hex color."""
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def get_256_color(self, color_index: int) -> str:
        """Get color for 256-color palette."""
        if color_index < 16:
            return self.STANDARD_COLORS[color_index]
        elif color_index < 232:
            # 216 color cube (6x6x6)
            color_index -= 16
            r = (color_index // 36) * 51
            g = ((color_index % 36) // 6) * 51
            b = (color_index % 6) * 51
            return self.rgb_to_hex(r, g, b)
        else:
            # 24 grayscale colors
            gray = 8 + (color_index - 232) * 10
            return self.rgb_to_hex(gray, gray, gray)
    
    def parse_color(self, params: List[int], is_background: bool = False) -> Optional[str]:
        """Parse color parameters and return hex color."""
        if not params:
            return None
        
        if params[0] == 2 and len(params) >= 4:
            # RGB color: 38;2;r;g;b or 48;2;r;g;b
            return self.rgb_to_hex(params[1], params[2], params[3])
        elif params[0] == 5 and len(params) >= 2:
            # 256-color: 38;5;n or 48;5;n
            return self.get_256_color(params[1])
        elif len(params) == 1:
            # Standard color
            color_num = params[0]
            if is_background:
                if 40 <= color_num <= 47:
                    return self.STANDARD_COLORS[color_num - 40]
                elif 100 <= color_num <= 107:
                    return self.STANDARD_COLORS[color_num - 100 + 8]
            else:
                if 30 <= color_num <= 37:
                    return self.STANDARD_COLORS[color_num - 30]
                elif 90 <= color_num <= 97:
                    return self.STANDARD_COLORS[color_num - 90 + 8]
        
        return None
    
    def handle_sgr(self, params: List[int]):
        """Handle Select Graphic Rendition (SGR) escape sequences."""
        if not params:
            params = [0]
        
        i = 0
        while i < len(params):
            param = params[i]
            
            if param == 0:
                # Reset all attributes
                self.state = TerminalState()
            elif param == 1:
                self.state.bold = True
            elif param == 2:
                self.state.dim = True
            elif param == 3:
                self.state.italic = True
            elif param == 4:
                self.state.underline = True
            elif param == 5 or param == 6:
                self.state.blink = True
            elif param == 7:
                self.state.reverse = True
            elif param == 8:
                self.state.hidden = True
            elif param == 9:
                self.state.strikethrough = True
            elif param == 22:
                self.state.bold = False
                self.state.dim = False
            elif param == 23:
                self.state.italic = False
            elif param == 24:
                self.state.underline = False
            elif param == 25:
                self.state.blink = False
            elif param == 27:
                self.state.reverse = False
            elif param == 28:
                self.state.hidden = False
            elif param == 29:
                self.state.strikethrough = False
            elif 30 <= param <= 37:
                # Foreground color
                self.state.fg_color = self.STANDARD_COLORS[param - 30]
            elif param == 38:
                # Extended foreground color
                if i + 1 < len(params):
                    color_params = []
                    if params[i + 1] == 2 and i + 4 < len(params):
                        # RGB: 38;2;r;g;b
                        color_params = params[i + 1:i + 5]
                        i += 4
                    elif params[i + 1] == 5 and i + 2 < len(params):
                        # 256-color: 38;5;n
                        color_params = params[i + 1:i + 3]
                        i += 2
                    
                    if color_params:
                        self.state.fg_color = self.parse_color(color_params)
            elif param == 39:
                # Default foreground color
                self.state.fg_color = None
            elif 40 <= param <= 47:
                # Background color
                self.state.bg_color = self.STANDARD_COLORS[param - 40]
            elif param == 48:
                # Extended background color
                if i + 1 < len(params):
                    color_params = []
                    if params[i + 1] == 2 and i + 4 < len(params):
                        # RGB: 48;2;r;g;b
                        color_params = params[i + 1:i + 5]
                        i += 4
                    elif params[i + 1] == 5 and i + 2 < len(params):
                        # 256-color: 48;5;n
                        color_params = params[i + 1:i + 3]
                        i += 2
                    
                    if color_params:
                        self.state.bg_color = self.parse_color(color_params, is_background=True)
            elif param == 49:
                # Default background color
                self.state.bg_color = None
            elif 90 <= param <= 97:
                # Bright foreground colors
                self.state.fg_color = self.STANDARD_COLORS[param - 90 + 8]
            elif 100 <= param <= 107:
                # Bright background colors
                self.state.bg_color = self.STANDARD_COLORS[param - 100 + 8]
            
            i += 1
    
    def get_current_style(self) -> str:
        """Get CSS style string for current terminal state."""
        styles = []
        
        # Handle reverse video
        fg_color = self.state.fg_color
        bg_color = self.state.bg_color
        
        if self.state.reverse:
            fg_color, bg_color = bg_color, fg_color
        
        # Colors
        if fg_color:
            styles.append(f'color: {fg_color}')
        else:
            styles.append('color: #C0C0C0')  # Default terminal foreground
        
        if bg_color:
            styles.append(f'background-color: {bg_color}')
        
        # Text decorations
        if self.state.bold:
            styles.append('font-weight: bold')
        
        if self.state.dim:
            styles.append('opacity: 0.5')
        
        if self.state.italic:
            styles.append('font-style: italic')
        
        text_decorations = []
        if self.state.underline:
            text_decorations.append('underline')
        if self.state.strikethrough:
            text_decorations.append('line-through')
        
        if text_decorations:
            styles.append(f'text-decoration: {" ".join(text_decorations)}')
        
        if self.state.blink:
            styles.append('animation: blink 1s infinite')
        
        if self.state.hidden:
            styles.append('visibility: hidden')
        
        return '; '.join(styles)
    
    def process_csi_sequence(self, params_str: str, command: str):
        """Process CSI (Control Sequence Introducer) sequences."""
        params = []
        if params_str:
            try:
                params = [int(p) if p else 0 for p in params_str.split(';')]
            except ValueError:
                params = []
        
        if command == 'm':
            # SGR - Select Graphic Rendition
            self.handle_sgr(params)
        elif command in ['A', 'B', 'C', 'D']:
            # Cursor movement (we'll ignore for HTML rendering)
            pass
        elif command == 'H' or command == 'f':
            # Cursor position
            row = params[0] - 1 if params else 0
            col = params[1] - 1 if len(params) > 1 else 0
            self.cursor_row = max(0, row)
            self.cursor_col = max(0, col)
        elif command == 'J':
            # Erase display (we'll ignore for HTML rendering)
            pass
        elif command == 'K':
            # Erase line (we'll ignore for HTML rendering)
            pass
        elif command == 's':
            # Save cursor position
            self.saved_cursor = (self.cursor_row, self.cursor_col)
        elif command == 'u':
            # Restore cursor position
            self.cursor_row, self.cursor_col = self.saved_cursor
    
    def convert_to_html(self, text: str, title: str = "Terminal Output") -> str:
        """Convert ANSI text to HTML."""
        self.reset_state()
        
        # Limit input size to prevent excessive processing
        if len(text) > 50000:  # 50KB limit
            text = text[-50000:]  # Keep last 50KB
            text = "... (input truncated) ...\n" + text
        
        # Split text into lines for processing
        lines = text.split('\n')
        html_lines = []
        
        # Limit number of lines to prevent excessive processing
        max_lines = 1000
        if len(lines) > max_lines:
            lines = lines[-max_lines:]  # Keep last 1000 lines
            html_lines.append("... (lines truncated) ...")
        
        for line_num, line in enumerate(lines):
            try:
                # Limit line length to prevent excessive processing
                if len(line) > 2000:  # 2KB per line limit
                    line = line[:2000] + "... (line truncated)"
                
                html_line = self.convert_line_to_html(line)
                html_lines.append(html_line)
                
                # Safety check - if processing is taking too long, break
                if line_num > 0 and line_num % 100 == 0:
                    # Every 100 lines, check if we should continue
                    total_html_size = sum(len(l) for l in html_lines)
                    if total_html_size > 100000:  # 100KB HTML limit
                        html_lines.append("... (output truncated due to size) ...")
                        break
                        
            except Exception as e:
                # If a line fails to convert, add it as plain text
                html_lines.append(f"[Error converting line: {str(e)}]")
        
        # Generate complete HTML document
        css = self.generate_css()
        html_content = '\n'.join(html_lines)
        
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
    
    def convert_line_to_html(self, line: str) -> str:
        """Convert a single line of ANSI text to HTML."""
        result = []
        current_style = ""
        i = 0
        max_iterations = len(line) * 2  # Safety limit to prevent infinite loops
        iterations = 0
        
        while i < len(line) and iterations < max_iterations:
            iterations += 1
            
            # Look for ANSI escape sequences
            csi_match = self.CSI_PATTERN.match(line, i)
            if csi_match:
                # Process CSI sequence
                params_str, command = csi_match.groups()
                try:
                    self.process_csi_sequence(params_str, command)
                except Exception as e:
                    # Skip problematic escape sequences
                    pass
                i = csi_match.end()
                
                # Check if style changed
                new_style = self.get_current_style()
                if new_style != current_style:
                    if current_style:
                        result.append('</span>')
                    if new_style:
                        result.append(f'<span style="{new_style}">')
                    current_style = new_style
                continue
            
            # Look for OSC sequences (title setting, etc.)
            osc_match = self.OSC_PATTERN.match(line, i)
            if osc_match:
                # Skip OSC sequences for now
                i = osc_match.end()
                continue
            
            # Look for simple escape sequences
            simple_match = self.SIMPLE_ESCAPE_PATTERN.match(line, i)
            if simple_match:
                # Skip simple escape sequences
                i = simple_match.end()
                continue
            
            # Regular character
            char = line[i]
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
            elif ord(char) < 32 and char not in ['\n', '\r']:
                # Skip other control characters that aren't handled
                pass
            else:
                result.append(char)
            
            i += 1
        
        # Close any open span
        if current_style:
            result.append('</span>')
        
        return ''.join(result)
    
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
            white-space: pre-wrap;
            word-wrap: break-word;
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


def convert_ansi_to_html(text: str, title: str = "Terminal Output") -> str:
    """Convenience function to convert ANSI text to HTML."""
    converter = AnsiToHtmlConverter()
    return converter.convert_to_html(text, title)
