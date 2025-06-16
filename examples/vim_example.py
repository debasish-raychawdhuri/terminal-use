#!/usr/bin/env python3
"""Example of using the Terminal MCP Server with vim."""

import json
import sys
import time

import requests


def main():
    """Run the vim example."""
    base_url = "http://localhost:8000"
    
    # Create a temporary file to edit
    temp_file = "/tmp/vim_example.txt"
    
    # Start vim
    print(f"Starting vim to edit {temp_file}...")
    response = requests.post(
        f"{base_url}/run",
        json={"command": f"vim {temp_file}", "timeout": 60}
    ).json()
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print(f"Initial output:\n{response['output']}")
    
    # Wait a bit for vim to fully initialize
    time.sleep(1)
    
    # Get updated output
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    print(f"Updated output:\n{response['output']}")
    
    # Enter insert mode
    print("\nEntering insert mode...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": "i"}
    ).json()
    
    # Type some text
    print("Typing text...")
    text = "Hello, this is a test file created with vim through the Terminal MCP Server.\n\nThis demonstrates how AI agents can interact with terminal-based applications."
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": text}
    ).json()
    
    # Wait a bit for vim to process the input
    time.sleep(1)
    
    # Get updated output
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    print(f"After typing:\n{response['output']}")
    
    # Exit insert mode
    print("\nExiting insert mode...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": "\x1b"}  # Escape key
    ).json()
    
    # Save and quit
    print("Saving and quitting...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": ":wq\r"}
    ).json()
    
    # Wait a bit for vim to exit
    time.sleep(1)
    
    # Check if vim has exited
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    if not response["running"]:
        print(f"vim exited with code: {response['exit_code']}")
        print(f"File {temp_file} has been created and saved.")
    else:
        print("vim is still running, terminating session...")
        requests.delete(f"{base_url}/sessions/{session_id}")


if __name__ == "__main__":
    main()
