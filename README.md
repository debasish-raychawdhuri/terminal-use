# Terminal MCP Server

A Model Context Protocol (MCP) server that allows AI agents to interact with terminal-based applications, especially TUI (Terminal User Interface) applications that require interactive input.

## Purpose

This MCP server acts as a bridge between AI agents (like Amazon Q and Windsurf) and terminal-based interactive applications. It solves the problem of agents hanging when trying to directly run interactive terminal applications.

## Features

- Run terminal-based interactive applications in a controlled environment
- Send keystrokes and commands to running applications
- Capture terminal output for AI agent processing
- Support for common TUI applications (vim, nano, htop, less, top, etc.)
- Timeout mechanisms to prevent hanging
- **Terminal emulator support** for truly interactive TUI applications
- **Full MCP protocol compliance** for seamless integration with AI agents

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux environment (tested on Ubuntu/Debian)
- Terminal emulators: xterm, gnome-terminal, konsole, or tmux
- Required Python packages: pexpect, asyncio

### From Source

```bash
# Clone the repository
git clone https://github.com/debasish-raychawdhuri/terminal-use.git
cd terminal-use

# Install dependencies (optional - server runs without installation)
pip install pexpect
```

## MCP Client Setup

### Amazon Q CLI Setup

1. **Configure Amazon Q CLI** to use the terminal MCP server:

```json
{
  "mcpServers": {
    "terminal": {
      "command": "/home/debasish/work/talentica/terminal-mcp-server/start_mcp_server.sh"
    }
  }
}
```

2. **Verify the setup**:
   - The server should load without the "failed to load" error
   - You should see terminal-related tools available in Amazon Q

### Windsurf Setup

1. **Configure Windsurf** to use the terminal MCP server:

```json
{
  "mcpServers": {
    "terminal": {
      "command": "/usr/bin/python",
      "args": ["/home/debasish/work/talentica/terminal-mcp-server/run_server.py"]
    }
  }
}
```

2. **Verify the setup**:
   - Windsurf should successfully connect to the MCP server
   - Terminal tools should be available in the Windsurf interface

## Available Tools

The MCP server provides the following tools to AI agents:

### 1. `run_command`
Run a command in a terminal session.

**Parameters:**
- `command` (required): The command to execute
- `timeout` (optional): Timeout in seconds (default: 30)
- `session_id` (optional): Reuse existing session
- `use_terminal_emulator` (optional): Use terminal emulator for TUI apps
- `terminal_emulator` (optional): Specify emulator (xterm, gnome-terminal, konsole, tmux)

### 2. `send_input`
Send input to a running terminal session.

**Parameters:**
- `session_id` (required): The terminal session ID
- `input` (required): Input text to send

### 3. `get_session`
Get the current state and output of a terminal session.

**Parameters:**
- `session_id` (required): The terminal session ID
- `raw_output` (optional): Return raw output with ANSI codes

### 4. `terminate_session`
Terminate a specific terminal session.

**Parameters:**
- `session_id` (required): The terminal session ID to terminate

### 5. `list_sessions`
List all active terminal sessions.

**Parameters:** None

### 6. `get_session_html`
Get the current state of a terminal session rendered as HTML with proper ANSI color and formatting support.

**Parameters:**
- `session_id` (required): The terminal session ID
- `title` (optional): Title for the HTML document (default: "Terminal Output")

**Features:**
- **Full ANSI support**: 16 standard colors, 256-color palette, and RGB colors
- **Text formatting**: Bold, italic, underline, strikethrough, blink, reverse video
- **Background colors**: Full support for background color sequences
- **Complete output**: No truncation - full terminal output is preserved
- **Complete HTML**: Generates full HTML documents with CSS styling
- **Terminal styling**: Authentic terminal appearance with monospace fonts

## Usage Examples

### Basic Command Execution

```bash
# AI agent can run simple commands
run_command(command="ls -la /tmp")
run_command(command="ps aux | grep python")
```

### Interactive TUI Applications

```bash
# Run vim in a terminal emulator
run_command(
    command="vim /tmp/myfile.txt",
    use_terminal_emulator=True,
    terminal_emulator="xterm"
)

# Send keystrokes to vim
send_input(session_id="<session_id>", input="i")  # Enter insert mode
send_input(session_id="<session_id>", input="Hello World!")  # Type text
send_input(session_id="<session_id>", input="\x1b")  # Press Escape
send_input(session_id="<session_id>", input=":wq\n")  # Save and quit
```

### Session Management

```bash
# Check session status
get_session(session_id="<session_id>")

# List all sessions
list_sessions()

# Get HTML representation of terminal session
get_session_html(session_id="<session_id>", title="My Terminal Session")

# Clean up
terminate_session(session_id="<session_id>")
```

### HTML Terminal Rendering

The `get_session_html` tool provides rich HTML rendering of terminal sessions:

```bash
# Run a colorful command
run_command(command="ls --color=always")

# Get the HTML representation
html_content = get_session_html(session_id="<session_id>", title="Colorful Directory Listing")

# The HTML includes:
# - Full ANSI color support (16 colors, 256-color palette, RGB)
# - Text formatting (bold, italic, underline, strikethrough)
# - Background colors and reverse video
# - Authentic terminal styling with monospace fonts
# - Complete HTML document ready for display or saving
```

**HTML Features:**
- **Complete output**: No truncation - full terminal output is preserved
- **Full color fidelity**: All ANSI colors converted accurately to HTML
- **Error handling**: Graceful fallback to plain text if conversion fails
- **Performance**: Optimized processing for reliable operation
- **Compatibility**: Works with all terminal applications and TUI programs

## Troubleshooting

### Amazon Q CLI Issues

**Problem**: `✗ terminal has failed to load after 0.0X s`

**Solutions**:
1. Ensure the shell script is executable: `chmod +x start_mcp_server.sh`
2. Verify Python path: `which python3`
3. Check file permissions and paths
4. Try the alternative Python command configuration

**Problem**: "No such file or directory" error

**Solutions**:
1. Use absolute paths in the configuration
2. Verify the repository is cloned to the correct location
3. Check that all files exist: `ls -la /home/debasish/work/talentica/terminal-mcp-server/`

### Windsurf Issues

**Problem**: MCP server connection fails

**Solutions**:
1. Check that PYTHONPATH is set correctly
2. Verify the working directory is correct
3. Try the shell script approach instead of the bash command

### General Issues

**Problem**: Terminal emulator not found

**Solutions**:
1. Install required terminal emulator: `sudo apt install xterm`
2. Use tmux for headless environments: `sudo apt install tmux`
3. Specify a different emulator in the command

**Problem**: Permission denied errors

**Solutions**:
1. Make scripts executable: `chmod +x *.sh`
2. Check file ownership: `ls -la`
3. Ensure proper directory permissions

### HTML Rendering Issues

**Problem**: Windsurf hangs when using `get_session_html`

**Solutions**:
1. Use the diagnostic script: `python3 windsurf_debug.py`
2. Try the minimal server configuration first
3. Check browser developer console for errors
4. Verify terminal session has reasonable output size

**Problem**: HTML output appears incorrect

**Solutions**:
1. Check that terminal session contains ANSI escape sequences
2. Use `get_session(raw_output=True)` to verify raw output
3. Test with simple colored commands first: `echo -e '\\033[31mRed\\033[0m'`
4. Save HTML to file and open in browser for inspection

**Problem**: HTML generation is slow

**Solutions**:
1. HTML conversion is optimized for performance
2. Large terminal outputs are processed efficiently
3. Consider using `get_session` for text-only output if HTML is not needed

## Development

### File Structure

```
terminal-mcp-server/
├── terminal_mcp_server/
│   ├── main.py              # Main MCP server implementation
│   ├── terminal_manager.py  # Terminal session management
│   ├── terminal_emulator.py # Terminal emulator integration
│   └── screen_buffer.py     # Screen content processing
├── start_mcp_server.sh      # Shell script for Q CLI
├── run_server.py           # Python wrapper for Q CLI
├── README.md               # This file
└── pyproject.toml          # Package configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both Amazon Q CLI and Windsurf
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs with `Q_LOG_LEVEL=trace` for Amazon Q
3. Open an issue on GitHub with detailed error information
