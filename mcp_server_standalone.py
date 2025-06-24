#!/usr/bin/env python3
"""
Persistent MCP server that maintains sessions between calls.
This fixes the session persistence issue Amazon Q was experiencing.
"""

import json
import sys
import os
import logging
import time
import signal
import select
import subprocess
import uuid
import pickle
import atexit
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the terminal emulator
from terminal_mcp_server.terminal_emulator import TerminalEmulatorSession, detect_terminal_emulator

# Set up detailed logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class PersistentTerminalManager:
    def __init__(self):
        self.sessions = {}
        self.emulator_sessions = {}
        self.session_file = Path("/tmp/mcp_terminal_sessions.pkl")
        
        # Load existing sessions on startup
        self._load_sessions()
        
        # Register cleanup handler
        atexit.register(self._cleanup_all_sessions)
    
    def _save_sessions(self):
        """Save session metadata to disk (not the actual session objects)"""
        try:
            session_data = {
                'session_ids': list(self.sessions.keys()) + list(self.emulator_sessions.keys()),
                'timestamp': time.time()
            }
            with open(self.session_file, 'wb') as f:
                pickle.dump(session_data, f)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def _load_sessions(self):
        """Load session metadata from disk"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'rb') as f:
                    session_data = pickle.load(f)
                    
                # Check if sessions are recent (within 1 hour)
                if time.time() - session_data.get('timestamp', 0) < 3600:
                    logger.error(f"Loaded {len(session_data.get('session_ids', []))} session IDs from disk")
                else:
                    logger.error("Sessions too old, starting fresh")
                    self.session_file.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    
    def _cleanup_all_sessions(self):
        """Clean up all sessions on exit"""
        logger.error("Cleaning up all sessions...")
        for session in self.emulator_sessions.values():
            try:
                session.terminate()
            except:
                pass
        try:
            self.session_file.unlink(missing_ok=True)
        except:
            pass
    
    def generate_session_id(self) -> str:
        return str(uuid.uuid4())
    
    def run_command(self, command: str, session_id: str, timeout: int = 30, *args, **kwargs) -> Tuple[str, Optional[int], bool]:
        """Run a simple command (non-interactive)"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout + result.stderr
            self.sessions[session_id] = {
                'command': command,
                'output': output,
                'exit_code': result.returncode,
                'running': False
            }
            self._save_sessions()
            return output, result.returncode, False
        except subprocess.TimeoutExpired:
            output = "Command timed out"
            self.sessions[session_id] = {
                'command': command,
                'output': output,
                'exit_code': -1,
                'running': False
            }
            self._save_sessions()
            return output, -1, False
        except Exception as e:
            output = f"Error: {str(e)}"
            self.sessions[session_id] = {
                'command': command,
                'output': output,
                'exit_code': -1,
                'running': False
            }
            self._save_sessions()
            return output, -1, False
    
    def start_terminal_emulator(self, command: str, session_id: str, timeout: int = 30) -> Tuple[str, Optional[int], bool]:
        """Start an interactive terminal emulator session."""
        try:
            emulator = detect_terminal_emulator()
            session = TerminalEmulatorSession(command, timeout=timeout, emulator=emulator)
            self.emulator_sessions[session_id] = session
            self._save_sessions()
            logger.error(f"Created terminal session {session_id} with emulator {emulator}")
            return f"Terminal emulator started with command: {command}\nSession ID: {session_id}\nEmulator: {emulator}", None, True
        except Exception as e:
            logger.error(f"Error starting terminal emulator: {e}")
            return f"Error starting terminal emulator: {str(e)}", -1, False
    
    def send_input_to_terminal(self, session_id: str, input_text: str) -> Tuple[str, Optional[int], bool]:
        """Send input to a terminal emulator session."""
        logger.error(f"Sending input '{repr(input_text)}' to session {session_id}")
        
        if session_id not in self.emulator_sessions:
            available_sessions = list(self.emulator_sessions.keys())
            logger.error(f"Session {session_id} not found. Available sessions: {available_sessions}")
            return f"Session {session_id} not found. Available sessions: {available_sessions}", -1, False
        
        session = self.emulator_sessions[session_id]
        if not session.is_running():
            logger.error(f"Session {session_id} is not running")
            return f"Session {session_id} is not running", session.exit_code, False
        
        try:
            # Parse escape sequences from JSON strings
            parsed_input = self._parse_escape_sequences(input_text)
            logger.error(f"Parsed input: {repr(parsed_input)}")
            
            session.send_input(parsed_input)
            output = session.get_output()
            logger.error(f"Input sent successfully to session {session_id}")
            return output, session.exit_code, session.is_running()
        except Exception as e:
            logger.error(f"Error sending input to session {session_id}: {e}")
            return f"Error sending input: {str(e)}", -1, session.is_running()
    
    def _parse_escape_sequences(self, text: str) -> str:
        """Parse escape sequences from JSON string format to actual characters."""
        # Handle common escape sequences that come from JSON
        replacements = {
            '\\x1b': '\x1b',  # Escape character
            '\\r': '\r',      # Carriage return  
            '\\n': '\n',      # Newline
            '\\t': '\t',      # Tab
            '\\\\': '\\',     # Literal backslash
            '\\u001b': '\x1b', # Unicode escape for ESC
            '\\033': '\x1b',   # Octal escape for ESC
        }
        
        result = text
        for escape_seq, actual_char in replacements.items():
            result = result.replace(escape_seq, actual_char)
        
        return result
    
    def get_terminal_output(self, session_id: str) -> Tuple[str, Optional[int], bool]:
        """Get output from a terminal emulator session."""
        if session_id not in self.emulator_sessions:
            return f"Session {session_id} not found", -1, False
        
        session = self.emulator_sessions[session_id]
        output = session.get_output()
        return output, session.exit_code, session.is_running()
    
    def capture_screen(self, session_id: str) -> Tuple[str, Optional[int], bool]:
        """Capture the current screen content of a terminal session."""
        if session_id not in self.emulator_sessions:
            return f"Session {session_id} not found", -1, False
        
        session = self.emulator_sessions[session_id]
        if not session.is_running():
            return f"Session {session_id} is not running", session.exit_code, False
        
        try:
            screen_content = session.capture_screen()
            return screen_content, session.exit_code, session.is_running()
        except Exception as e:
            return f"Error capturing screen: {str(e)}", -1, session.is_running()
    
    def terminate_terminal(self, session_id: str) -> Tuple[str, Optional[int], bool]:
        """Terminate a terminal emulator session."""
        if session_id not in self.emulator_sessions:
            return f"Session {session_id} not found", -1, False
        
        session = self.emulator_sessions[session_id]
        session.terminate()
        del self.emulator_sessions[session_id]
        self._save_sessions()
        logger.error(f"Terminated session {session_id}")
        return f"Terminal session {session_id} terminated", 0, False
    
    def list_sessions(self) -> List[str]:
        all_sessions = list(self.sessions.keys()) + list(self.emulator_sessions.keys())
        logger.error(f"Available sessions: {all_sessions}")
        return all_sessions

# Global instance that persists across requests
terminal_manager = PersistentTerminalManager()

def get_tools():
    """Get the available tools."""
    return [
        {
            "name": "run_command",
            "description": "Execute a shell command (non-interactive)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "start_terminal",
            "description": "Start an interactive terminal emulator with a command",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run in the terminal emulator"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "send_input",
            "description": "Send input to an interactive terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID of the terminal"
                    },
                    "input": {
                        "type": "string",
                        "description": "The input to send (text, escape sequences, etc.)"
                    }
                },
                "required": ["session_id", "input"]
            }
        },
        {
            "name": "get_output",
            "description": "Get current output from a terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID of the terminal"
                    }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "capture_screen",
            "description": "Capture the current screen content of a terminal session (works best with tmux)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID of the terminal to capture"
                    }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "terminate_terminal",
            "description": "Terminate a terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID of the terminal to terminate"
                    }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "list_sessions",
            "description": "List all command sessions",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]

def handle_request(request: Dict) -> Dict:
    """Handle a JSON-RPC request."""
    logger.error(f"Processing request: {request}")
    
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})
    
    try:
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "terminal-mcp-server-persistent",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": get_tools()
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "run_command":
                session_id = terminal_manager.generate_session_id()
                output, exit_code, running = terminal_manager.run_command(
                    arguments["command"],
                    session_id,
                    30
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Command: {arguments['command']}\nSession: {session_id}\nExit Code: {exit_code}\n\nOutput:\n{output}"
                            }
                        ]
                    }
                }
            elif tool_name == "start_terminal":
                session_id = terminal_manager.generate_session_id()
                timeout = arguments.get("timeout", 30)
                output, exit_code, running = terminal_manager.start_terminal_emulator(
                    arguments["command"],
                    session_id,
                    timeout
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output
                            }
                        ]
                    }
                }
            elif tool_name == "send_input":
                output, exit_code, running = terminal_manager.send_input_to_terminal(
                    arguments["session_id"],
                    arguments["input"]
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Input sent. Running: {running}\nOutput:\n{output}"
                            }
                        ]
                    }
                }
            elif tool_name == "get_output":
                output, exit_code, running = terminal_manager.get_terminal_output(
                    arguments["session_id"]
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Session running: {running}\nOutput:\n{output}"
                            }
                        ]
                    }
                }
            elif tool_name == "capture_screen":
                output, exit_code, running = terminal_manager.capture_screen(
                    arguments["session_id"]
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Screen capture for session {arguments['session_id']}:\n\n{output}"
                            }
                        ]
                    }
                }
            elif tool_name == "terminate_terminal":
                output, exit_code, running = terminal_manager.terminate_terminal(
                    arguments["session_id"]
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output
                            }
                        ]
                    }
                }
            elif tool_name == "list_sessions":
                sessions = terminal_manager.list_sessions()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Sessions: {', '.join(sessions) if sessions else 'None'}"
                            }
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        logger.error(f"Sending response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": f"Server error: {str(e)}"
            }
        }

def main():
    """Main server loop - stays running and maintains sessions."""
    logger.error("=== PERSISTENT MCP SERVER STARTING ===")
    logger.error(f"Python: {sys.executable}")
    logger.error(f"Working directory: {os.getcwd()}")
    logger.error(f"Script location: {__file__}")
    
    try:
        logger.error("Waiting for input...")
        
        # This loop keeps the server running and maintains sessions
        for line in sys.stdin:
            line = line.strip()
            logger.error(f"Received input: {repr(line)}")
            
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = handle_request(request)
                response_json = json.dumps(response)
                print(response_json, flush=True)
                logger.error(f"Response sent: {response_json}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Error handling request: {e}", exc_info=True)
                
    except KeyboardInterrupt:
        logger.error("Server interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.error("=== PERSISTENT MCP SERVER SHUTTING DOWN ===")

if __name__ == "__main__":
    main()