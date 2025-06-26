"""
Simple and direct color display for tkinter text widget.
"""

import tkinter as tk
import re
from typing import List, Tuple


class SimpleColorDisplay:
    """Simple color display that actually works with tkinter."""
    
    def __init__(self, text_widget: tk.Text):
        """Initialize the color display.
        
        Args:
            text_widget: The tkinter Text widget
        """
        self.text_widget = text_widget
        
        # Configure basic color tags
        self._setup_color_tags()
    
    def _setup_color_tags(self):
        """Set up color tags in the text widget."""
        # Standard colors
        self.text_widget.tag_configure("red", foreground="#FF0000")
        self.text_widget.tag_configure("green", foreground="#00FF00")
        self.text_widget.tag_configure("blue", foreground="#0000FF")
        self.text_widget.tag_configure("yellow", foreground="#FFFF00")
        self.text_widget.tag_configure("magenta", foreground="#FF00FF")
        self.text_widget.tag_configure("cyan", foreground="#00FFFF")
        self.text_widget.tag_configure("white", foreground="#FFFFFF")
        self.text_widget.tag_configure("black", foreground="#000000")
        
        # Bright colors
        self.text_widget.tag_configure("bright_red", foreground="#FF5555")
        self.text_widget.tag_configure("bright_green", foreground="#55FF55")
        self.text_widget.tag_configure("bright_blue", foreground="#5555FF")
        self.text_widget.tag_configure("bright_yellow", foreground="#FFFF55")
        self.text_widget.tag_configure("bright_magenta", foreground="#FF55FF")
        self.text_widget.tag_configure("bright_cyan", foreground="#55FFFF")
        
        # Bold
        self.text_widget.tag_configure("bold", font=("Courier New", 10, "bold"))
        
        # Combined tags
        self.text_widget.tag_configure("bold_red", foreground="#FF0000", font=("Courier New", 10, "bold"))
        self.text_widget.tag_configure("bold_green", foreground="#00FF00", font=("Courier New", 10, "bold"))
        self.text_widget.tag_configure("bold_blue", foreground="#0000FF", font=("Courier New", 10, "bold"))
        self.text_widget.tag_configure("bold_yellow", foreground="#FFFF00", font=("Courier New", 10, "bold"))
    
    def display_with_colors(self, content: str):
        """Display content with colors by parsing ANSI sequences.
        
        Args:
            content: Raw content with ANSI escape sequences
        """
        # Enable editing
        self.text_widget.configure(state=tk.NORMAL)
        
        # Clear existing content
        self.text_widget.delete(1.0, tk.END)
        
        # Process content and insert with colors
        self._process_and_insert(content)
        
        # Disable editing
        self.text_widget.configure(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
    
    def _process_and_insert(self, content: str):
        """Process content and insert with appropriate color tags.
        
        Args:
            content: Raw content with ANSI sequences
        """
        # Remove most escape sequences but keep color ones
        # First, let's handle the most common color sequences
        
        # Split content by ANSI color sequences
        parts = re.split(r'(\x1b\[[0-9;]*m)', content)
        
        current_color = None
        current_bold = False
        
        for part in parts:
            if part.startswith('\x1b[') and part.endswith('m'):
                # This is a color sequence
                color_code = part[2:-1]  # Remove \x1b[ and m
                current_color, current_bold = self._parse_color_code(color_code)
            else:
                # This is text content
                if part:  # Only insert non-empty parts
                    # Clean the text of other escape sequences
                    clean_text = self._clean_text(part)
                    if clean_text:
                        # Insert with appropriate tag
                        tag = self._get_tag_name(current_color, current_bold)
                        if tag:
                            self.text_widget.insert(tk.END, clean_text, tag)
                        else:
                            self.text_widget.insert(tk.END, clean_text)
    
    def _parse_color_code(self, code: str) -> Tuple[str, bool]:
        """Parse ANSI color code.
        
        Args:
            code: Color code (e.g., "31", "1;31")
            
        Returns:
            Tuple of (color_name, is_bold)
        """
        if not code or code == '0':
            return None, False
        
        codes = [int(c) for c in code.split(';') if c.isdigit()]
        
        color = None
        bold = False
        
        for c in codes:
            if c == 0:  # Reset
                color = None
                bold = False
            elif c == 1:  # Bold
                bold = True
            elif c == 31:  # Red
                color = "red"
            elif c == 32:  # Green
                color = "green"
            elif c == 33:  # Yellow
                color = "yellow"
            elif c == 34:  # Blue
                color = "blue"
            elif c == 35:  # Magenta
                color = "magenta"
            elif c == 36:  # Cyan
                color = "cyan"
            elif c == 37:  # White
                color = "white"
            elif c == 91:  # Bright red
                color = "bright_red"
            elif c == 92:  # Bright green
                color = "bright_green"
            elif c == 93:  # Bright yellow
                color = "bright_yellow"
            elif c == 94:  # Bright blue
                color = "bright_blue"
            elif c == 95:  # Bright magenta
                color = "bright_magenta"
            elif c == 96:  # Bright cyan
                color = "bright_cyan"
        
        return color, bold
    
    def _get_tag_name(self, color: str, bold: bool) -> str:
        """Get the appropriate tag name for color and formatting.
        
        Args:
            color: Color name
            bold: Whether text is bold
            
        Returns:
            Tag name or None
        """
        if not color:
            return "bold" if bold else None
        
        if bold and color in ["red", "green", "blue", "yellow"]:
            return f"bold_{color}"
        else:
            return color
    
    def _clean_text(self, text: str) -> str:
        """Clean text of non-color escape sequences while preserving TUI colors.
        
        Args:
            text: Raw text that may contain escape sequences
            
        Returns:
            Cleaned text with colors preserved
        """
        # Remove control/positioning sequences but KEEP color sequences
        # This preserves TUI app colors while removing positioning artifacts
        
        # Remove OSC sequences (Operating System Command) - titles, etc.
        text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', '', text)
        
        # Remove cursor positioning and movement (but keep colors)
        text = re.sub(r'\x1b\[[0-9;]*[HfABCDEFGJKST]', '', text)
        
        # Remove screen clearing commands
        text = re.sub(r'\x1b\[2J', '', text)
        text = re.sub(r'\x1b\[K', '', text)
        
        # Remove cursor visibility commands
        text = re.sub(r'\x1b\[\?25[hl]', '', text)
        
        # Remove mode setting (but not color modes)
        text = re.sub(r'\x1b\[\?[0-9]+[hl]', '', text)
        
        # Remove DCS, APC, PM sequences
        text = re.sub(r'\x1bP[^\x1b]*\x1b\\', '', text)
        text = re.sub(r'\x1b_[^\x1b]*\x1b\\', '', text)
        text = re.sub(r'\x1b\^[^\x1b]*\x1b\\', '', text)
        
        # Remove single character escape sequences
        text = re.sub(r'\x1b[()][AB012]', '', text)
        text = re.sub(r'\x1b[=>]', '', text)
        text = re.sub(r'\x1b[78]', '', text)
        text = re.sub(r'\x1b[DEHMNOVWXYZ]', '', text)
        
        # Remove most control characters (but keep newline, carriage return, tab)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # NOTE: We deliberately DO NOT remove \x1b[...m sequences (colors)
        # This preserves TUI application colors
        
        return text
