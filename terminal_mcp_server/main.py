"""Main entry point for the Terminal MCP Server."""

import argparse
import json
import logging
import os
import sys
import asyncio
import uuid
from typing import Dict, List, Optional, AsyncGenerator, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, Response, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from terminal_mcp_server.terminal_manager import TerminalManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Terminal MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

terminal_manager = TerminalManager()


# Middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.debug(f"Request: {request.method} {request.url.path}")
    
    # Log request headers
    headers_log = "\n".join([f"{k}: {v}" for k, v in request.headers.items()])
    logger.debug(f"Request headers:\n{headers_log}")
    
    # For POST requests, try to log the body
    if request.method == "POST":
        try:
            body = await request.body()
            logger.debug(f"Request body: {body.decode()}")
            # Reset the request body
            request._body = body
        except Exception as e:
            logger.error(f"Error reading request body: {e}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response status
    logger.debug(f"Response status: {response.status_code}")
    
    return response


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


class GetSessionRequest(BaseModel):
    """Request model for getting the state of a terminal session."""
    
    session_id: str
    raw_output: Optional[bool] = None


class TerminalResponse(BaseModel):
    """Response model for terminal operations."""
    
    session_id: str
    output: str
    exit_code: Optional[int] = None
    running: bool


class InitializeRequest(BaseModel):
    """Request model for MCP initialization."""
    client_name: str
    client_version: str


@app.post("/run", response_model=TerminalResponse)
async def run_command(request: RunCommandRequest):
    """Run a command in a terminal."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or terminal_manager.generate_session_id()
        
        # Run the command
        output, exit_code, running = terminal_manager.run_command(
            request.command, session_id, request.timeout, 
            request.use_terminal_emulator, request.terminal_emulator
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
async def get_session(session_id: str, raw_output: Optional[bool] = None):
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


# Store active MCP connections
mcp_connections = {}


@app.get("/mcp/manifest")
@app.get("/manifest")  # Also support without the /mcp prefix
async def mcp_manifest():
    """Return the MCP manifest for this server as a Server-Sent Event."""
    logger.info("Received request for MCP manifest")
    
    async def generate():
        # First send the manifest without an event type
        manifest = {
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
        
        manifest_json = json.dumps(manifest)
        logger.debug(f"Sending manifest data: {manifest_json[:100]}...")
        yield f"data: {manifest_json}\n\n"
        
        # Then immediately send the ready event
        logger.debug("Sending ready event")
        yield "event: ready\ndata: {}\n\n"
        
        # Keep connection alive with heartbeats
        counter = 0
        while True:
            await asyncio.sleep(3)
            counter += 1
            logger.debug(f"Sending heartbeat event #{counter}")
            yield "event: heartbeat\ndata: {}\n\n"
    
    # Set response headers for SSE
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disable buffering for nginx
    }
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers=headers
    )


@app.post("/mcp/initialize")
@app.post("/initialize")  # Also support without the /mcp prefix
async def mcp_initialize(request: Request):
    """Initialize the MCP connection."""
    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"MCP initialize request body: {body}")
        
        client_name = body.get("client_name", "unknown")
        client_version = body.get("client_version", "unknown")
        
        logger.info(f"MCP initialize request from {client_name} {client_version}")
        
        # Generate a connection ID
        connection_id = str(uuid.uuid4())
        
        # Store connection info
        mcp_connections[connection_id] = {
            "client_name": client_name,
            "client_version": client_version,
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Return success response
        response = {
            "connection_id": connection_id,
            "server_info": {
                "name": "terminal-mcp-server",
                "version": "0.1.0"
            }
        }
        logger.info(f"MCP initialize response: {response}")
        
        # Return with specific headers
        return JSONResponse(
            content=response,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        logger.error(f"Error in MCP initialize: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/events/{connection_id}")
@app.post("/events/{connection_id}")  # Also support without the /mcp prefix
async def mcp_events(connection_id: str, request: Request):
    """Handle MCP events for a specific connection."""
    # Check if connection exists
    if connection_id not in mcp_connections:
        # Be more lenient - create the connection if it doesn't exist
        logger.warning(f"Connection not found: {connection_id}, creating new connection")
        mcp_connections[connection_id] = {
            "client_name": "unknown",
            "client_version": "unknown",
            "created_at": asyncio.get_event_loop().time()
        }
    
    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"Received MCP event for connection {connection_id}: {body}")
        
        # Check if this is a JSON-RPC style request (Windsurf style)
        if "id" in body and "method" in body:
            # Handle JSON-RPC style request
            request_id = body.get("id")
            method = body.get("method")
            params = body.get("params", {})
            
            logger.info(f"Received JSON-RPC request: id={request_id}, method={method}")
            logger.debug(f"Params: {params}")
            
            # Handle initialize method
            if method == "initialize":
                client_capabilities = params.get("clientCapabilities", {})
                logger.info(f"Client capabilities: {client_capabilities}")
                
                # Return server info and capabilities
                return {
                    "id": request_id,
                    "result": {
                        "serverInfo": {
                            "name": "terminal-mcp-server",
                            "version": "0.1.0"
                        },
                        "capabilities": {
                            "commands": ["run_command", "send_input", "get_session", "terminate_session", "list_sessions"],
                            "supportedSchemaVersion": "v1"
                        }
                    }
                }
            else:
                logger.warning(f"Unknown JSON-RPC method: {method}")
                return {
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        # Handle standard MCP event format
        event_type = body.get("type")
        payload = body.get("payload", {})
        
        logger.info(f"Received MCP event: {event_type} for connection {connection_id}")
        logger.debug(f"Event payload: {payload}")
        
        # Handle different event types
        if event_type == "invoke_tool":
            tool_name = payload.get("name")
            tool_params = payload.get("parameters", {})
            
            logger.info(f"Invoking tool: {tool_name} with params: {tool_params}")
            
            # Handle tool invocation based on tool name
            if tool_name == "run_command":
                result = await run_command(RunCommandRequest(**tool_params))
                return {"result": result.dict()}
            elif tool_name == "send_input":
                result = await send_input(SendInputRequest(**tool_params))
                return {"result": result.dict()}
            elif tool_name == "get_session":
                result = await get_session(tool_params["session_id"], tool_params.get("raw_output"))
                return {"result": result.dict()}
            elif tool_name == "terminate_session":
                result = await terminate_session(tool_params["session_id"])
                return {"result": result}
            elif tool_name == "list_sessions":
                result = await list_sessions()
                return {"result": result}
            else:
                logger.warning(f"Unknown tool: {tool_name}")
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
            raise HTTPException(status_code=400, detail=f"Unknown event type: {event_type}")
    except Exception as e:
        logger.error(f"Error handling MCP event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the server."""
    parser = argparse.ArgumentParser(description="Terminal MCP Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    
    logger.info(f"Starting Terminal MCP Server on {args.host}:{args.port}")
    
    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
