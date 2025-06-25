"""Complete ANSI color and formatting definitions."""

# Standard 16 colors (0-15)
ANSI_COLORS = {
    # Basic colors (0-7)
    0: '#000000',   # Black
    1: '#800000',   # Dark Red
    2: '#008000',   # Dark Green
    3: '#808000',   # Dark Yellow
    4: '#000080',   # Dark Blue
    5: '#800080',   # Dark Magenta
    6: '#008080',   # Dark Cyan
    7: '#C0C0C0',   # Light Gray
    
    # Bright colors (8-15)
    8: '#808080',   # Dark Gray
    9: '#FF0000',   # Red
    10: '#00FF00',  # Green
    11: '#FFFF00',  # Yellow
    12: '#0000FF',  # Blue
    13: '#FF00FF',  # Magenta
    14: '#00FFFF',  # Cyan
    15: '#FFFFFF',  # White
    
    # Extended colors for direct mapping
    30: '#000000',  # Black foreground
    31: '#800000',  # Red foreground
    32: '#008000',  # Green foreground
    33: '#808000',  # Yellow foreground
    34: '#000080',  # Blue foreground
    35: '#800080',  # Magenta foreground
    36: '#008080',  # Cyan foreground
    37: '#C0C0C0',  # White foreground
    
    # Bright foreground colors (90-97)
    90: '#808080',  # Bright Black
    91: '#FF0000',  # Bright Red
    92: '#00FF00',  # Bright Green
    93: '#FFFF00',  # Bright Yellow
    94: '#0000FF',  # Bright Blue
    95: '#FF00FF',  # Bright Magenta
    96: '#00FFFF',  # Bright Cyan
    97: '#FFFFFF',  # Bright White
    
    # Background colors (40-47)
    40: '#000000',  # Black background
    41: '#800000',  # Red background
    42: '#008000',  # Green background
    43: '#808000',  # Yellow background
    44: '#000080',  # Blue background
    45: '#800080',  # Magenta background
    46: '#008080',  # Cyan background
    47: '#C0C0C0',  # White background
    
    # Bright background colors (100-107)
    100: '#808080', # Bright Black background
    101: '#FF0000', # Bright Red background
    102: '#00FF00', # Bright Green background
    103: '#FFFF00', # Bright Yellow background
    104: '#0000FF', # Bright Blue background
    105: '#FF00FF', # Bright Magenta background
    106: '#00FFFF', # Bright Cyan background
    107: '#FFFFFF', # Bright White background
}

def get_256_color(color_index: int) -> str:
    """Get color for 256-color palette (0-255)."""
    if color_index < 16:
        return ANSI_COLORS.get(color_index, '#C0C0C0')
    elif color_index < 232:
        # 216 color cube (6x6x6)
        color_index -= 16
        r = (color_index // 36) * 51
        g = ((color_index % 36) // 6) * 51
        b = (color_index % 6) * 51
        return f'#{r:02x}{g:02x}{b:02x}'
    else:
        # 24 grayscale colors (232-255)
        gray = 8 + (color_index - 232) * 10
        gray = min(255, gray)
        return f'#{gray:02x}{gray:02x}{gray:02x}'

def get_rgb_color(r: int, g: int, b: int) -> str:
    """Get RGB color."""
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f'#{r:02x}{g:02x}{b:02x}'

def parse_sgr_params(params_str: str) -> dict:
    """Parse SGR parameters and return formatting state."""
    if not params_str:
        params = [0]
    else:
        try:
            params = [int(p) if p else 0 for p in params_str.split(';')]
        except ValueError:
            params = [0]
    
    state = {
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
    
    i = 0
    while i < len(params):
        param = params[i]
        
        if param == 0:
            # Reset all
            state = {k: False if k != 'fg_color' and k != 'bg_color' else None for k in state}
        elif param == 1:
            state['bold'] = True
        elif param == 2:
            state['dim'] = True
        elif param == 3:
            state['italic'] = True
        elif param == 4:
            state['underline'] = True
        elif param == 5 or param == 6:
            state['blink'] = True
        elif param == 7:
            state['reverse'] = True
        elif param == 8:
            state['hidden'] = True
        elif param == 9:
            state['strikethrough'] = True
        elif param == 22:
            state['bold'] = False
            state['dim'] = False
        elif param == 23:
            state['italic'] = False
        elif param == 24:
            state['underline'] = False
        elif param == 25:
            state['blink'] = False
        elif param == 27:
            state['reverse'] = False
        elif param == 28:
            state['hidden'] = False
        elif param == 29:
            state['strikethrough'] = False
        elif 30 <= param <= 37:
            # Standard foreground colors
            color_idx = param - 30
            if state['bold']:
                # Bold + basic color = bright color
                state['fg_color'] = ANSI_COLORS[color_idx + 8]
            else:
                state['fg_color'] = ANSI_COLORS[color_idx]
        elif param == 38:
            # Extended foreground color
            if i + 1 < len(params):
                if params[i + 1] == 2 and i + 4 < len(params):
                    # RGB: 38;2;r;g;b
                    r, g, b = params[i + 2], params[i + 3], params[i + 4]
                    state['fg_color'] = get_rgb_color(r, g, b)
                    i += 4
                elif params[i + 1] == 5 and i + 2 < len(params):
                    # 256-color: 38;5;n
                    state['fg_color'] = get_256_color(params[i + 2])
                    i += 2
        elif param == 39:
            # Default foreground
            state['fg_color'] = None
        elif 40 <= param <= 47:
            # Standard background colors
            color_idx = param - 40
            if state['bold']:
                # Bold + basic background = bright background
                state['bg_color'] = ANSI_COLORS[color_idx + 8]
            else:
                state['bg_color'] = ANSI_COLORS[color_idx]
        elif param == 48:
            # Extended background color
            if i + 1 < len(params):
                if params[i + 1] == 2 and i + 4 < len(params):
                    # RGB: 48;2;r;g;b
                    r, g, b = params[i + 2], params[i + 3], params[i + 4]
                    state['bg_color'] = get_rgb_color(r, g, b)
                    i += 4
                elif params[i + 1] == 5 and i + 2 < len(params):
                    # 256-color: 48;5;n
                    state['bg_color'] = get_256_color(params[i + 2])
                    i += 2
        elif param == 49:
            # Default background
            state['bg_color'] = None
        elif 90 <= param <= 97:
            # Bright foreground colors
            state['fg_color'] = ANSI_COLORS[param]
        elif 100 <= param <= 107:
            # Bright background colors
            state['bg_color'] = ANSI_COLORS[param]
        
        i += 1
    
    return state

def format_css_style(state: dict) -> str:
    """Convert formatting state to CSS style string."""
    styles = []
    
    # Handle reverse video
    fg_color = state['fg_color']
    bg_color = state['bg_color']
    
    if state['reverse']:
        fg_color, bg_color = bg_color, fg_color
    
    # Colors
    if fg_color:
        styles.append(f'color: {fg_color}')
    else:
        styles.append('color: #C0C0C0')  # Default terminal foreground
    
    if bg_color:
        styles.append(f'background-color: {bg_color}')
    
    # Text formatting
    if state['bold']:
        styles.append('font-weight: bold')
    
    if state['dim']:
        styles.append('opacity: 0.5')
    
    if state['italic']:
        styles.append('font-style: italic')
    
    text_decorations = []
    if state['underline']:
        text_decorations.append('underline')
    if state['strikethrough']:
        text_decorations.append('line-through')
    
    if text_decorations:
        styles.append(f'text-decoration: {" ".join(text_decorations)}')
    
    if state['blink']:
        styles.append('animation: blink 1s infinite')
    
    if state['hidden']:
        styles.append('visibility: hidden')
    
    return '; '.join(styles)
