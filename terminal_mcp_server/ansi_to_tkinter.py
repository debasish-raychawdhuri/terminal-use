"""
ANSI escape sequence to tkinter text widget converter with color support.
"""

import re
import tkinter as tk
from typing import List, Tuple, Dict, Optional


class ANSIToTkinter:
    """Converts ANSI escape sequences to tkinter text widget with colors."""
    
    # ANSI color codes to tkinter colors
    ANSI_COLORS = {
        # Standard colors (30-37, 90-97)
        30: '#000000',  # Black
        31: '#CD0000',  # Red
        32: '#00CD00',  # Green
        33: '#CDCD00',  # Yellow
        34: '#0000EE',  # Blue
        35: '#CD00CD',  # Magenta
        36: '#00CDCD',  # Cyan
        37: '#E5E5E5',  # White
        
        # Bright colors (90-97)
        90: '#7F7F7F',  # Bright Black (Gray)
        91: '#FF0000',  # Bright Red
        92: '#00FF00',  # Bright Green
        93: '#FFFF00',  # Bright Yellow
        94: '#5C5CFF',  # Bright Blue
        95: '#FF00FF',  # Bright Magenta
        96: '#00FFFF',  # Bright Cyan
        97: '#FFFFFF',  # Bright White
    }
    
    # Background colors (40-47, 100-107)
    ANSI_BG_COLORS = {
        40: '#000000',  # Black
        41: '#CD0000',  # Red
        42: '#00CD00',  # Green
        43: '#CDCD00',  # Yellow
        44: '#0000EE',  # Blue
        45: '#CD00CD',  # Magenta
        46: '#00CDCD',  # Cyan
        47: '#E5E5E5',  # White
        
        # Bright background colors (100-107)
        100: '#7F7F7F',  # Bright Black
        101: '#FF0000',  # Bright Red
        102: '#00FF00',  # Bright Green
        103: '#FFFF00',  # Bright Yellow
        104: '#5C5CFF',  # Bright Blue
        105: '#FF00FF',  # Bright Magenta
        106: '#00FFFF',  # Bright Cyan
        107: '#FFFFFF',  # Bright White
    }
    
    def __init__(self, text_widget: tk.Text):
        """Initialize the ANSI to tkinter converter.
        
        Args:
            text_widget: The tkinter Text widget to update
        """
        self.text_widget = text_widget
        self.current_fg = 'white'  # Default foreground
        self.current_bg = 'black'  # Default background
        self.current_bold = False
        self.current_underline = False
        self.tag_counter = 0
        
        # Configure default tags
        self.text_widget.tag_configure('default', foreground='white', background='black')
    
    def clear_and_insert_with_colors(self, content: str):
        """Clear the text widget and insert content with ANSI color support.
        
        Args:
            content: Raw terminal content with ANSI escape sequences
        """
        try:
            # Enable editing
            self.text_widget.configure(state=tk.NORMAL)
            
            # Clear existing content
            self.text_widget.delete(1.0, tk.END)
            
            # Reset formatting state
            self.current_fg = 'white'
            self.current_bg = 'black'
            self.current_bold = False
            self.current_underline = False
            self.tag_counter = 0
            
            # Process and insert content with colors
            self._process_ansi_content(content)
            
            # Disable editing
            self.text_widget.configure(state=tk.DISABLED)
            
            # Auto-scroll to bottom
            self.text_widget.see(tk.END)
            
        except Exception as e:
            print(f"[ANSI] Error in clear_and_insert_with_colors: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _process_ansi_content(self, content: str):
        """Process ANSI content and insert into text widget with colors.
        
        Args:
            content: Raw content with ANSI escape sequences
        """
        # Comprehensive pattern to match all ANSI escape sequences
        ansi_pattern = re.compile(r'''
            \x1b\[                    # ESC[
            [0-9;?]*                  # Parameters (numbers, semicolons, question marks)
            [a-zA-Z]                  # Command letter
            |                         # OR
            \x1b\]                    # ESC] (OSC sequences)
            [^\x07\x1b]*             # Any chars except BEL or ESC
            (?:\x07|\x1b\\)           # Terminated by BEL or ESC\
            |                         # OR
            \x1b[()][AB012]           # Character set sequences
            |                         # OR
            \x1b[=>]                  # Application keypad sequences
            |                         # OR
            \x1b[78]                  # Save/restore cursor
            |                         # OR
            \x1b\[[0-9;]*[~]          # Function key sequences
        ''', re.VERBOSE)
        
        pos = 0
        while pos < len(content):
            # Find next ANSI sequence
            match = ansi_pattern.search(content, pos)
            
            if match:
                # Insert text before the ANSI sequence
                if match.start() > pos:
                    text_chunk = content[pos:match.start()]
                    self._insert_text_with_current_style(text_chunk)
                
                # Process the ANSI sequence
                full_sequence = match.group(0)
                self._handle_full_ansi_sequence(full_sequence)
                
                pos = match.end()
            else:
                # Insert remaining text
                remaining_text = content[pos:]
                self._insert_text_with_current_style(remaining_text)
                break
    
    def _handle_full_ansi_sequence(self, sequence: str):
        """Handle a complete ANSI escape sequence.
        
        Args:
            sequence: The full ANSI sequence (e.g., '\x1b[31m')
        """
        if sequence.startswith('\x1b[') and sequence.endswith('m'):
            # SGR (color/style) sequence
            params = sequence[2:-1]  # Remove \x1b[ and m
            self._handle_sgr_sequence(params)
        elif sequence.startswith('\x1b]'):
            # OSC sequence - ignore (these are often shell integration sequences)
            pass
        elif sequence.startswith('\x1b[') and len(sequence) > 2:
            # Other CSI sequences
            command = sequence[-1]
            params = sequence[2:-1]
            self._handle_csi_sequence(params, command)
        # All other sequences are ignored (filtered out)
    
    def _handle_csi_sequence(self, params: str, command: str):
        """Handle CSI (Control Sequence Introducer) sequences.
        
        Args:
            params: Parameter string
            command: Command character
        """
        if command == 'J':  # Clear screen
            pass  # Ignore
        elif command == 'H':  # Cursor position
            pass  # Ignore
        elif command in ['A', 'B', 'C', 'D']:  # Cursor movement
            pass  # Ignore
        elif command == 'K':  # Clear line
            pass  # Ignore
        elif command in ['h', 'l']:  # Set/reset mode
            pass  # Ignore
        elif command == 's':  # Save cursor
            pass  # Ignore
        elif command == 'u':  # Restore cursor
            pass  # Ignore
        # All other CSI sequences are ignored
    
    def _insert_text_with_current_style(self, text: str):
        """Insert text with current formatting style.
        
        Args:
            text: Text to insert
        """
        if not text:
            return
        
        # Create a unique tag for this style
        tag_name = f"style_{self.tag_counter}"
        self.tag_counter += 1
        
        # Configure the tag with current style
        font_config = ('Courier New', 10)
        if self.current_bold:
            font_config = ('Courier New', 10, 'bold')
        if self.current_underline:
            if self.current_bold:
                font_config = ('Courier New', 10, 'bold', 'underline')
            else:
                font_config = ('Courier New', 10, 'underline')
        
        self.text_widget.tag_configure(
            tag_name,
            foreground=self.current_fg,
            background=self.current_bg,
            font=font_config
        )
        
        # Insert text with the tag
        self.text_widget.insert(tk.END, text, tag_name)
    
    def _handle_sgr_sequence(self, params: str):
        """Handle SGR (color/style) ANSI sequence.
        
        Args:
            params: SGR parameters (e.g., "1;31;42")
        """
        if not params:
            params = '0'  # Default to reset
        
        codes = [int(p) for p in params.split(';') if p.isdigit()]
        
        for code in codes:
            if code == 0:  # Reset
                self.current_fg = 'white'
                self.current_bg = 'black'
                self.current_bold = False
                self.current_underline = False
            elif code == 1:  # Bold
                self.current_bold = True
            elif code == 4:  # Underline
                self.current_underline = True
            elif code == 22:  # Normal intensity (not bold)
                self.current_bold = False
            elif code == 24:  # Not underlined
                self.current_underline = False
            elif 30 <= code <= 37:  # Foreground colors
                self.current_fg = self.ANSI_COLORS.get(code, 'white')
            elif 40 <= code <= 47:  # Background colors
                self.current_bg = self.ANSI_BG_COLORS.get(code, 'black')
            elif 90 <= code <= 97:  # Bright foreground colors
                self.current_fg = self.ANSI_COLORS.get(code, 'white')
            elif 100 <= code <= 107:  # Bright background colors
                self.current_bg = self.ANSI_BG_COLORS.get(code, 'black')


def convert_ansi_to_2d_with_colors(text: str, width: int = 120, height: int = 40) -> str:
    """Convert ANSI text to 2D layout while preserving color information.
    
    This function processes ANSI sequences to maintain both layout and color info.
    
    Args:
        text: Raw terminal text with ANSI sequences
        width: Terminal width
        height: Terminal height
        
    Returns:
        Processed text with ANSI color sequences preserved in proper 2D layout
    """
    # For now, we'll use the existing 2D converter but preserve more ANSI sequences
    from .ansi_to_text_2d import Terminal2DTextRenderer
    
    # Create a modified renderer that preserves color sequences
    renderer = Terminal2DTextRenderer(width, height)
    
    # Process the text but keep color sequences
    processed_text = renderer.process_text(text)
    
    return processed_text
