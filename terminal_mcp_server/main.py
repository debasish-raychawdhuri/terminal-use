"""Main entry point for the Terminal MCP Server."""

import argparse
import logging
import os
import sys
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from terminal_mcp_server.terminal_manager import TerminalManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Terminal MCP Server")
terminal_manager = TerminalManager()


class RunCommandRequest(BaseModel):
    """Request model for running a command."""
    
    command: str
    timeout: Optional[int] = 30
    session_id: Optional[str] = None
    use_terminal_emulator: Optional[bool] = True
    terminal_emulator: Optional[str] = None  # If None, auto-detect


class SendInputRequest(BaseModel):
    """Request model for sending input to a running terminal session."""
    
    input: str
    session_id: str


class TerminalResponse(BaseModel):
    """Response model for terminal operations."""
    
    session_id: str
    output: str
    exit_code: Optional[int] = None
    running: bool


@app.post("/run", response_model=TerminalResponse)
async def run_command(request: RunCommandRequest):
    """Run a command in a terminal and return the output."""
    try:
        session_id = request.session_id or terminal_manager.generate_session_id()
        output, exit_code, running = terminal_manager.run_command(
            request.command, 
            session_id, 
            request.timeout,
            use_terminal_emulator=request.use_terminal_emulator,
            terminal_emulator=request.terminal_emulator
        )
        return TerminalResponse(
            session_id=session_id,
            output=output,
            exit_code=exit_code,
            running=running,
        )
    except Exception as e:
        logger.error(f"Error running command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_input", response_model=TerminalResponse)
async def send_input(request: SendInputRequest):
    """Send input to a running terminal session."""
    try:
        output, exit_code, running = terminal_manager.send_input(
            request.session_id, request.input
        )
        return TerminalResponse(
            session_id=request.session_id,
            output=output,
            exit_code=exit_code,
            running=running,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error sending input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=TerminalResponse)
async def get_session(session_id: str, raw_output: bool = Query(None)):
    """Get the current state of a terminal session."""
    try:
        output, exit_code, running = terminal_manager.get_session_state(
            session_id, raw_output=raw_output
        )
        return TerminalResponse(
            session_id=session_id,
            output=output,
            exit_code=exit_code,
            running=running,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def terminate_session(session_id: str):
    """Terminate a terminal session."""
    try:
        terminal_manager.terminate_session(session_id)
        return {"message": f"Session {session_id} terminated"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions", response_model=List[str])
async def list_sessions():
    """List all active terminal sessions."""
    return terminal_manager.list_sessions()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/mcp/manifest")
async def mcp_manifest():
    """Return the MCP manifest for this server."""
    return {
        "schema_version": "v1",
        "name": "terminal-use",
        "display_name": "Terminal Use",
        "description": "Allows AI agents to interact with terminal-based applications",
        "tools": [
            {
                "name": "run_command",
                "description": "Run a command in a terminal",
                "input_schema": {
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
                            "enum": ["xterm", "gnome-terminal", "konsole", "tmux", None],
                            "default": None
                        }
                    },
                    "required": ["command"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for the terminal session"
                        },
                        "output": {
                            "type": "string",
                            "description": "The output from the terminal"
                        },
                        "exit_code": {
                            "type": "integer",
                            "description": "The exit code of the command, if completed"
                        },
                        "running": {
                            "type": "boolean",
                            "description": "Whether the command is still running"
                        }
                    }
                }
            },
            {
                "name": "send_input",
                "description": "Send input to a running terminal session",
                "input_schema": {
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
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for the terminal session"
                        },
                        "output": {
                            "type": "string",
                            "description": "The output from the terminal after sending input"
                        },
                        "exit_code": {
                            "type": "integer",
                            "description": "The exit code of the command, if completed"
                        },
                        "running": {
                            "type": "boolean",
                            "description": "Whether the command is still running"
                        }
                    }
                }
            },
            {
                "name": "get_session",
                "description": "Get the current state of a terminal session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for the terminal session"
                        },
                        "raw_output": {
                            "type": "boolean",
                            "description": "Whether to return raw output with ANSI escape sequences",
                            "default": None
                        }
                    },
                    "required": ["session_id"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for the terminal session"
                        },
                        "output": {
                            "type": "string",
                            "description": "The current output from the terminal"
                        },
                        "exit_code": {
                            "type": "integer",
                            "description": "The exit code of the command, if completed"
                        },
                        "running": {
                            "type": "boolean",
                            "description": "Whether the command is still running"
                        }
                    }
                }
            },
            {
                "name": "terminate_session",
                "description": "Terminate a terminal session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for the terminal session to terminate"
                        }
                    },
                    "required": ["session_id"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Confirmation message"
                        }
                    }
                }
            },
            {
                "name": "list_sessions",
                "description": "List all active terminal sessions",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                },
                "output_schema": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of active session IDs"
                }
            }
        ]
    }


def main():
    """Run the Terminal MCP Server."""
    parser = argparse.ArgumentParser(description="Terminal MCP Server")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level",
    )
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    logger.info(f"Starting Terminal MCP Server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
