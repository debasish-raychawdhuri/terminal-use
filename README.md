# Terminal MCP Server

A Model Context Protocol (MCP) server that allows AI agents to interact with terminal-based applications, especially TUI (Terminal User Interface) applications that require interactive input.

## Purpose

This MCP server acts as a bridge between AI agents (like Amazon Q) and terminal-based interactive applications. It solves the problem of agents hanging when trying to directly run interactive terminal applications.

## Features

- Run terminal-based interactive applications in a controlled environment
- Send keystrokes and commands to running applications
- Capture terminal output for AI agent processing
- Support for common TUI applications (vim, nano, htop, less, top, etc.)
- Timeout mechanisms to prevent hanging
- **Terminal emulator support** for truly interactive TUI applications

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/terminal-mcp-server.git
cd terminal-mcp-server

# Install the package
pip install -e .
```

### Using Docker

```bash
# Build the Docker image
docker build -t terminal-mcp-server .

# Run the container
docker run -p 8000:8000 terminal-mcp-server
```

## Usage

### Starting the Server

```bash
# Start the server on localhost:8000 (default)
terminal-mcp-server

# Start the server on a specific host and port
terminal-mcp-server --host 0.0.0.0 --port 8080

# Set log level
terminal-mcp-server --log-level debug
```

### Testing the Server

The repository includes test scripts to verify the server's functionality:

```bash
# Test basic features
python test_features.py

# Test specific feature
python test_features.py --test vim

# Test TUI applications
python test_tui_applications.py

# Test specific TUI application
python test_tui_applications.py --test htop
```

### Terminal Emulator Support

For truly interactive TUI applications, the server can launch them in a separate terminal emulator window:

```bash
# Run the TUI example
python examples/tui_example.py

# Specify a terminal emulator
python examples/tui_example.py --emulator xterm

# Test a specific application
python examples/tui_example.py --app htop
```

Supported terminal emulators:
- xterm
- gnome-terminal
- konsole
- tmux (for headless environments)

### API Endpoints

- `POST /run` - Run a command in a terminal
- `POST /send_input` - Send input to a running terminal session
- `GET /sessions/{session_id}` - Get the current state of a terminal session
- `DELETE /sessions/{session_id}` - Terminate a terminal session
- `GET /sessions` - List all active terminal sessions
- `GET /mcp/manifest` - MCP protocol manifest

### Example Usage

```python
import requests

# Start a terminal session with a terminal emulator
response = requests.post(
    "http://localhost:8000/run",
    json={
        "command": "vim /tmp/test.txt", 
        "timeout": 30,
        "use_terminal_emulator": True
    }
).json()

session_id = response["session_id"]
print(f"Session ID: {session_id}")
print("vim is now running in a separate terminal window")

# Wait for user interaction
input("Press Enter after editing the file...")

# Terminate the session
requests.delete(f"http://localhost:8000/sessions/{session_id}")
```

## Integration with AI Agents

AI agents can use this MCP server through the Model Context Protocol. The server provides a manifest at `/mcp/manifest` that describes the available tools.

## How It Works

The server provides two modes of operation:

1. **Direct Mode**: Uses pexpect to spawn processes directly. Good for simple commands and basic interaction.

2. **Terminal Emulator Mode**: Launches a separate terminal emulator window for the application. This is ideal for TUI applications that require a full terminal environment.

In Terminal Emulator Mode, the server:
- Launches a terminal emulator (xterm, gnome-terminal, etc.)
- Runs the command inside that terminal
- Uses a socket for communication between the server and the application
- Can send keystrokes to the terminal window using xdotool or similar tools
