"""ANSI escape sequence to HTML converter with proper 2D terminal screen handling."""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TerminalCell:
    """Represents a single character cell in the terminal."""
    char: str = ' '
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


class Terminal2DRenderer:
    """Renders ANSI escape sequences to HTML with proper 2D terminal layout."""
    
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
    CSI_PATTERN = re.compile(r'\x1b\[([0-9;?]*)([a-zA-Z])')
    
    def __init__(self, width: int = 120, height: int = 40):
        """Initialize the terminal renderer."""
        self.width = width
        self.height = height
        self.reset_terminal()
    
    def reset_terminal(self):
        """Reset the terminal state."""
        # Create 2D grid of terminal cells
        self.screen = [[TerminalCell() for _ in range(self.width)] for _ in range(self.height)]
        
        # Current cursor position
        self.cursor_row = 0
        self.cursor_col = 0
        
        # Current formatting state
        self.current_fg = None
        self.current_bg = None
        self.current_bold = False
        self.current_dim = False
        self.current_italic = False
        self.current_underline = False
        self.current_strikethrough = False
        self.current_blink = False
        self.current_reverse = False
        self.current_hidden = False
    
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
            return f'#{r:02x}{g:02x}{b:02x}'
        else:
            # 24 grayscale colors
            gray = 8 + (color_index - 232) * 10
            return f'#{gray:02x}{gray:02x}{gray:02x}'
    
    def handle_sgr(self, params: List[int]):
        """Handle Select Graphic Rendition (SGR) escape sequences."""
        if not params:
            params = [0]
        
        i = 0
        while i < len(params):
            param = params[i]
            
            if param == 0:
                # Reset all attributes
                self.current_fg = None
                self.current_bg = None
                self.current_bold = False
                self.current_dim = False
                self.current_italic = False
                self.current_underline = False
                self.current_strikethrough = False
                self.current_blink = False
                self.current_reverse = False
                self.current_hidden = False
            elif param == 1:
                self.current_bold = True
            elif param == 2:
                self.current_dim = True
            elif param == 3:
                self.current_italic = True
            elif param == 4:
                self.current_underline = True
            elif param == 5 or param == 6:
                self.current_blink = True
            elif param == 7:
                self.current_reverse = True
            elif param == 8:
                self.current_hidden = True
            elif param == 9:
                self.current_strikethrough = True
            elif param == 22:
                self.current_bold = False
                self.current_dim = False
            elif param == 23:
                self.current_italic = False
            elif param == 24:
                self.current_underline = False
            elif param == 25:
                self.current_blink = False
            elif param == 27:
                self.current_reverse = False
            elif param == 28:
                self.current_hidden = False
            elif param == 29:
                self.current_strikethrough = False
            elif 30 <= param <= 37:
                # Foreground color
                self.current_fg = self.STANDARD_COLORS[param - 30]
            elif param == 38:
                # Extended foreground color
                if i + 1 < len(params):
                    if params[i + 1] == 2 and i + 4 < len(params):
                        # RGB: 38;2;r;g;b
                        r, g, b = params[i + 2], params[i + 3], params[i + 4]
                        self.current_fg = f'#{r:02x}{g:02x}{b:02x}'
                        i += 4
                    elif params[i + 1] == 5 and i + 2 < len(params):
                        # 256-color: 38;5;n
                        self.current_fg = self.get_256_color(params[i + 2])
                        i += 2
            elif param == 39:
                # Default foreground color
                self.current_fg = None
            elif 40 <= param <= 47:
                # Background color
                self.current_bg = self.STANDARD_COLORS[param - 40]
            elif param == 48:
                # Extended background color
                if i + 1 < len(params):
                    if params[i + 1] == 2 and i + 4 < len(params):
                        # RGB: 48;2;r;g;b
                        r, g, b = params[i + 2], params[i + 3], params[i + 4]
                        self.current_bg = f'#{r:02x}{g:02x}{b:02x}'
                        i += 4
                    elif params[i + 1] == 5 and i + 2 < len(params):
                        # 256-color: 48;5;n
                        self.current_bg = self.get_256_color(params[i + 2])
                        i += 2
            elif param == 49:
                # Default background color
                self.current_bg = None
            elif 90 <= param <= 97:
                # Bright foreground colors
                self.current_fg = self.STANDARD_COLORS[param - 90 + 8]
            elif 100 <= param <= 107:
                # Bright background colors
                self.current_bg = self.STANDARD_COLORS[param - 100 + 8]
            
            i += 1
    
    def handle_cursor_position(self, params: List[int]):
        """Handle cursor positioning (CUP) sequences."""
        if not params:
            row, col = 1, 1
        elif len(params) == 1:
            row, col = params[0], 1
        else:
            row, col = params[0], params[1]
        
        # Convert to 0-based indexing and clamp to screen bounds
        self.cursor_row = max(0, min(self.height - 1, row - 1))
        self.cursor_col = max(0, min(self.width - 1, col - 1))
    
    def put_char(self, char: str):
        """Put a character at the current cursor position with current formatting."""
        if 0 <= self.cursor_row < self.height and 0 <= self.cursor_col < self.width:
            cell = self.screen[self.cursor_row][self.cursor_col]
            cell.char = char
            cell.fg_color = self.current_fg
            cell.bg_color = self.current_bg
            cell.bold = self.current_bold
            cell.dim = self.current_dim
            cell.italic = self.current_italic
            cell.underline = self.current_underline
            cell.strikethrough = self.current_strikethrough
            cell.blink = self.current_blink
            cell.reverse = self.current_reverse
            cell.hidden = self.current_hidden
            
            # Advance cursor
            self.cursor_col += 1
            if self.cursor_col >= self.width:
                self.cursor_col = 0
                self.cursor_row += 1
    
    def process_text(self, text: str):
        """Process ANSI text and populate the terminal screen."""
        i = 0
        while i < len(text):
            # Look for ANSI escape sequences
            match = self.CSI_PATTERN.match(text, i)
            if match:
                params_str, command = match.groups()
                
                # Parse parameters
                params = []
                if params_str:
                    try:
                        # Handle parameters with ? prefix
                        clean_params = params_str.lstrip('?')
                        if clean_params:
                            params = [int(p) if p else 0 for p in clean_params.split(';')]
                    except ValueError:
                        params = []
                
                # Handle different commands
                if command == 'm':
                    # SGR - Select Graphic Rendition
                    self.handle_sgr(params)
                elif command in ['H', 'f']:
                    # CUP - Cursor Position
                    self.handle_cursor_position(params)
                elif command == 'A':
                    # CUU - Cursor Up
                    count = params[0] if params else 1
                    self.cursor_row = max(0, self.cursor_row - count)
                elif command == 'B':
                    # CUD - Cursor Down
                    count = params[0] if params else 1
                    self.cursor_row = min(self.height - 1, self.cursor_row + count)
                elif command == 'C':
                    # CUF - Cursor Forward
                    count = params[0] if params else 1
                    self.cursor_col = min(self.width - 1, self.cursor_col + count)
                elif command == 'D':
                    # CUB - Cursor Back
                    count = params[0] if params else 1
                    self.cursor_col = max(0, self.cursor_col - count)
                # Ignore other sequences for now (terminal modes, etc.)
                
                i = match.end()
            else:
                # Regular character
                char = text[i]
                if char == '\r':
                    # Carriage return - move to beginning of line
                    self.cursor_col = 0
                elif char == '\n':
                    # Line feed - move to next line
                    self.cursor_row += 1
                    if self.cursor_row >= self.height:
                        self.cursor_row = self.height - 1
                elif char == '\t':
                    # Tab - advance to next tab stop (every 8 columns)
                    next_tab = ((self.cursor_col // 8) + 1) * 8
                    self.cursor_col = min(self.width - 1, next_tab)
                elif ord(char) >= 32:  # Printable character
                    self.put_char(char)
                
                i += 1
    
    def get_cell_style(self, cell: TerminalCell) -> str:
        """Get CSS style string for a terminal cell."""
        styles = []
        
        # Handle reverse video
        fg_color = cell.fg_color
        bg_color = cell.bg_color
        
        if cell.reverse:
            fg_color, bg_color = bg_color, fg_color
        
        # Colors
        if fg_color:
            styles.append(f'color: {fg_color}')
        else:
            styles.append('color: #C0C0C0')  # Default terminal foreground
        
        if bg_color:
            styles.append(f'background-color: {bg_color}')
        
        # Text formatting
        if cell.bold:
            styles.append('font-weight: bold')
        
        if cell.dim:
            styles.append('opacity: 0.5')
        
        if cell.italic:
            styles.append('font-style: italic')
        
        text_decorations = []
        if cell.underline:
            text_decorations.append('underline')
        if cell.strikethrough:
            text_decorations.append('line-through')
        
        if text_decorations:
            styles.append(f'text-decoration: {" ".join(text_decorations)}')
        
        if cell.blink:
            styles.append('animation: blink 1s infinite')
        
        if cell.hidden:
            styles.append('visibility: hidden')
        
        return '; '.join(styles)
    
    def render_to_html(self, title: str = "Terminal Output") -> str:
        """Render the terminal screen to HTML."""
        html_lines = []
        
        for row in self.screen:
            line_parts = []
            current_style = ""
            
            for cell in row:
                cell_style = self.get_cell_style(cell)
                
                if cell_style != current_style:
                    if current_style:
                        line_parts.append('</span>')
                    if cell_style:
                        line_parts.append(f'<span style="{cell_style}">')
                    current_style = cell_style
                
                # HTML escape the character
                char = cell.char
                if char == '<':
                    char = '&lt;'
                elif char == '>':
                    char = '&gt;'
                elif char == '&':
                    char = '&amp;'
                elif char == '"':
                    char = '&quot;'
                elif char == "'":
                    char = '&#39;'
                
                line_parts.append(char)
            
            # Close any open span
            if current_style:
                line_parts.append('</span>')
            
            html_lines.append(''.join(line_parts))
        
        # Remove trailing empty lines
        while html_lines and not html_lines[-1].strip():
            html_lines.pop()
        
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


def convert_ansi_to_html_2d(text: str, title: str = "Terminal Output", width: int = 120, height: int = 40) -> str:
    """Convert ANSI text to HTML with proper 2D terminal layout."""
    renderer = Terminal2DRenderer(width, height)
    renderer.process_text(text)
    return renderer.render_to_html(title)
