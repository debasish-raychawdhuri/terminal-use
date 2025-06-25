"""Main entry point for the Terminal MCP Server."""

import argparse
import json
import logging
import os
import sys
import asyncio
import uuid
import signal
import threading
import time
from typing import Dict, List, Optional, Any

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.ansi_to_html import convert_ansi_to_html

# Configure logging to stderr to avoid interfering with stdio communication
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

terminal_manager = TerminalManager()
def get_tools_definition():
    """Get the tools definition for MCP protocol."""
    return [
        {
            "name": "run_command",
            "description": "Run a command in a terminal",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 30
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID for the terminal session"
                    },
                    "use_terminal_emulator": {
                        "type": "boolean",
                        "description": "Whether to use a terminal emulator for TUI applications",
                        "default": True
                    },
                    "terminal_emulator": {
                        "type": "string",
                        "description": "Terminal emulator to use (xterm, gnome-terminal, konsole, tmux)",
                        "enum": ["xterm", "gnome-terminal", "konsole", "tmux"],
                        "default": None
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "send_input",
            "description": "Send input to a running terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID for the terminal session"
                    },
                    "input": {
                        "type": "string",
                        "description": "The input to send to the terminal"
                    }
                },
                "required": ["session_id", "input"]
            }
        },
        {
            "name": "get_session",
            "description": "Get the current state of a terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID for the terminal session"
                    },
                    "raw_output": {
                        "type": "boolean",
                        "description": "Whether to return raw output with ANSI escape sequences"
                    }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "terminate_session",
            "description": "Terminate a terminal session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID for the terminal session to terminate"
                    }
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "list_sessions",
            "description": "List all active terminal sessions",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_session_html",
            "description": "Get the current state of a terminal session rendered as HTML with proper ANSI color and formatting support",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID for the terminal session"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the HTML document",
                        "default": "Terminal Output"
                    }
                },
                "required": ["session_id"]
            }
        }
    ]
class MCPServer:
    """MCP Server using stdio JSON-RPC communication."""
    
    def __init__(self):
        self.terminal_manager = terminal_manager
        self.running = True
        self.initialized = False
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.error(f"Received signal {signum}, shutting down gracefully")
        self.running = False
        
    async def handle_request(self, request: dict) -> dict:
        """Handle a JSON-RPC request."""
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params", {})
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "terminal-use",
                            "version": "0.1.0"
                        }
                    }
                }
            
            elif method == "initialized":
                # This is a notification, no response needed
                logger.info("Received initialized notification")
                return None
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": get_tools_definition()
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "run_command":
                    session_id = tool_args.get("session_id") or self.terminal_manager.generate_session_id()
                    output, exit_code, running = self.terminal_manager.run_command(
                        tool_args["command"], 
                        session_id, 
                        tool_args.get("timeout", 30),
                        tool_args.get("use_terminal_emulator", False),
                        tool_args.get("terminal_emulator")
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": f"Session ID: {session_id}\nOutput:\n{output}\nExit Code: {exit_code}\nRunning: {running}"
                            }]
                        }
                    }
                
                elif tool_name == "send_input":
                    output, exit_code, running = self.terminal_manager.send_input(
                        tool_args["session_id"], tool_args["input"]
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": f"Output:\n{output}\nExit Code: {exit_code}\nRunning: {running}"
                            }]
                        }
                    }
                
                elif tool_name == "get_session":
                    try:
                        logger.info(f"Getting session state for {tool_args['session_id']}")
                        
                        # Check if session exists first
                        if tool_args["session_id"] not in self.terminal_manager.sessions:
                            logger.warning(f"Session {tool_args['session_id']} not found")
                            return {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "content": [{
                                        "type": "text",
                                        "text": f"Session {tool_args['session_id']} not found or has been terminated"
                                    }]
                                }
                            }
                        
                        # Get session state with timeout protection
                        session = self.terminal_manager.sessions[tool_args["session_id"]]
                        
                        # Quick check if session is still valid
                        if not hasattr(session, 'is_running'):
                            logger.error(f"Invalid session object for {tool_args['session_id']}")
                            return {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "content": [{
                                        "type": "text",
                                        "text": f"Session {tool_args['session_id']} is invalid"
                                    }]
                                }
                            }
                        
                        # Get the state quickly
                        running = session.is_running()
                        exit_code = getattr(session, 'exit_code', None)
                        
                        # Get output based on session type
                        raw_output = tool_args.get("raw_output", False)
                        if hasattr(session, 'get_screen_content') and not raw_output:
                            # TerminalEmulatorSession - use screen content
                            output = session.get_screen_content()[:5000]
                        elif hasattr(session, 'get_output'):
                            # TerminalEmulatorSession - use get_output method
                            output = session.get_output(raw=raw_output)[:5000]
                        else:
                            # TerminalSession - use output_buffer
                            if raw_output and hasattr(session, 'raw_output_buffer'):
                                output = session.raw_output_buffer[:5000]
                            else:
                                output = getattr(session, 'output_buffer', '')[:5000]
                        
                        logger.info(f"Got session state - output length: {len(output)}, running: {running}")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": f"Output:\n{output}\nExit Code: {exit_code}\nRunning: {running}"
                                }]
                            }
                        }
                        logger.info("Returning get_session response")
                        return response
                        
                    except KeyError as e:
                        logger.error(f"Session not found: {e}")
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": f"Session not found: {str(e)}"
                                }]
                            }
                        }
                    except Exception as e:
                        logger.error(f"Error in get_session: {e}")
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": f"Error getting session state: {str(e)}"
                                }]
                            }
                        }
                
                elif tool_name == "terminate_session":
                    self.terminal_manager.terminate_session(tool_args["session_id"])
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": f"Session {tool_args['session_id']} terminated"
                            }]
                        }
                    }
                
                elif tool_name == "list_sessions":
                    sessions = self.terminal_manager.list_sessions()
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": f"Active sessions: {', '.join(sessions) if sessions else 'None'}"
                            }]
                        }
                    }
                
                elif tool_name == "get_session_html":
                    try:
                        logger.debug(f"Getting session HTML for {tool_args['session_id']}")
                        
                        # Check if session exists first
                        if tool_args["session_id"] not in self.terminal_manager.sessions:
                            logger.debug(f"Session {tool_args['session_id']} not found")
                            return {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "result": {
                                    "content": [{
                                        "type": "text",
                                        "text": f"Session {tool_args['session_id']} not found or has been terminated"
                                    }]
                                }
                            }
                        
                        # Get session and raw output
                        session = self.terminal_manager.sessions[tool_args["session_id"]]
                        
                        # Get raw output with ANSI sequences, but limit size to prevent hanging
                        raw_output = ""
                        try:
                            if hasattr(session, 'get_screen_content'):
                                # TerminalEmulatorSession - use screen content
                                raw_output = session.get_screen_content()
                            elif hasattr(session, 'get_output'):
                                # TerminalEmulatorSession - use get_output method with raw=True
                                raw_output = session.get_output(raw=True)
                            else:
                                # TerminalSession - use raw_output_buffer
                                raw_output = getattr(session, 'raw_output_buffer', '')
                            
                            # Limit raw output size to prevent client hanging (max 10KB of raw terminal data)
                            if len(raw_output) > 10240:
                                raw_output = raw_output[-10240:]  # Keep last 10KB
                                raw_output = "... (output truncated) ...\n" + raw_output
                                
                        except Exception as e:
                            logger.debug(f"Error getting raw output: {e}")
                            raw_output = f"Error retrieving session output: {str(e)}"
                        
                        # Convert to HTML with size limits
                        title = tool_args.get("title", "Terminal Output")
                        try:
                            html_content = convert_ansi_to_html(raw_output, title)
                            
                            # Additional safety check - limit final HTML size (max 50KB)
                            if len(html_content) > 51200:
                                # If HTML is too large, provide a truncated version
                                truncated_raw = raw_output[:2048] if len(raw_output) > 2048 else raw_output
                                html_content = convert_ansi_to_html(
                                    truncated_raw + "\n\n... (HTML output truncated due to size) ...", 
                                    title
                                )
                            
                            logger.debug(f"Generated HTML content - length: {len(html_content)}")
                            
                        except Exception as e:
                            logger.debug(f"Error converting to HTML: {e}")
                            # Fallback to plain text if HTML conversion fails
                            html_content = f"""<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body><pre style="font-family: monospace; background: black; color: white; padding: 20px;">
Error converting ANSI to HTML: {str(e)}

Raw output:
{raw_output[:1000]}{'...' if len(raw_output) > 1000 else ''}
</pre></body></html>"""
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": html_content
                                }]
                            }
                        }
                        
                    except KeyError as e:
                        logger.debug(f"Session not found: {e}")
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": f"Session not found: {str(e)}"
                                }]
                            }
                        }
                    except Exception as e:
                        logger.debug(f"Error in get_session_html: {e}")
                        return {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": f"Error generating HTML: {str(e)}"
                                }]
                            }
                        }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": f"Server error: {str(e)}"
                }
            }
    
    def run_sync(self):
        """Run the MCP server using stdin/stdout synchronously."""
        logger.info("Starting MCP server with stdio transport")
        
        # Record start time for timeout check
        self.start_time = time.time()
        
        # Start input reader thread
        input_thread = threading.Thread(target=self._read_input, daemon=True)
        input_thread.start()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(0.1)
                
                # If we haven't been initialized after 30 seconds, that's probably an error
                if not self.initialized and time.time() - self.start_time > 30:
                    logger.error("No initialization received after 30 seconds, shutting down")
                    break
                    
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, exiting")
        except Exception as e:
            logger.error(f"Fatal error in server: {e}", exc_info=True)
        finally:
            logger.info("MCP server shutting down")
            self.running = False
    
    def _read_input(self):
        """Read input from stdin in a separate thread."""
        self.start_time = time.time()
        
        try:
            while self.running:
                try:
                    # Read line from stdin
                    line = sys.stdin.readline()
                    if not line:
                        # EOF reached, but don't exit immediately
                        # This might be normal behavior for some MCP clients
                        logger.info("Stdin EOF received")
                        time.sleep(1)  # Wait a bit before continuing
                        continue
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    logger.debug(f"Received request: {line}")
                    
                    # Parse JSON-RPC request
                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        # Send error response
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": f"Parse error: {str(e)}"
                            }
                        }
                        print(json.dumps(error_response), flush=True)
                        continue
                    
                    # Mark as initialized if this is an initialize request
                    if request.get("method") == "initialize":
                        self.initialized = True
                    
                    # Handle request synchronously
                    response = asyncio.run(self.handle_request(request))
                    
                    # Send response to stdout (only if there is a response)
                    if response is not None:
                        logger.debug(f"Sending response: {json.dumps(response)}")
                        print(json.dumps(response), flush=True)
                    else:
                        logger.debug("No response needed (notification)")
                    
                except Exception as e:
                    logger.error(f"Error in input reader: {e}", exc_info=True)
                    if not self.running:
                        break
                    continue
        except Exception as e:
            logger.error(f"Fatal error in input reader: {e}", exc_info=True)
        finally:
            logger.info("Input reader thread shutting down")
def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Terminal MCP Server")
    parser.add_argument("--log-level", type=str, default="error", help="Log level")
    parser.add_argument("--timeout", type=int, default=0, help="Server timeout in seconds (0 = no timeout)")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper(), logging.ERROR)
    logging.getLogger().setLevel(log_level)
    
    # Create and run the MCP server
    server = MCPServer()
    
    # Set timeout if specified
    if args.timeout > 0:
        def timeout_handler():
            time.sleep(args.timeout)
            logger.error(f"Server timeout after {args.timeout} seconds")
            server.running = False
        
        timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        timeout_thread.start()
    
    server.run_sync()


if __name__ == "__main__":
    main()
