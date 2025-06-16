#!/usr/bin/env python3
"""Example of using the Terminal MCP Server with htop."""

import json
import sys
import time

import requests


def main():
    """Run the htop example."""
    base_url = "http://localhost:8000"
    
    # Start htop
    print("Starting htop...")
    response = requests.post(
        f"{base_url}/run",
        json={"command": "htop", "timeout": 60}
    ).json()
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print(f"Initial output:\n{response['output']}")
    
    # Wait a bit for htop to fully initialize
    time.sleep(1)
    
    # Get updated output
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    print(f"Updated output:\n{response['output']}")
    
    # Send some keystrokes to interact with htop
    print("\nSending 'F2' to open setup...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": "\x1bOQ"}  # F2 key
    ).json()
    
    # Wait a bit for htop to respond
    time.sleep(1)
    
    # Get updated output
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    print(f"Setup screen:\n{response['output']}")
    
    # Send Escape to exit setup
    print("\nSending 'Escape' to exit setup...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": "\x1b"}  # Escape key
    ).json()
    
    # Wait a bit for htop to respond
    time.sleep(1)
    
    # Get updated output
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    print(f"Back to main screen:\n{response['output']}")
    
    # Send 'q' to quit htop
    print("\nSending 'q' to quit htop...")
    response = requests.post(
        f"{base_url}/send_input",
        json={"session_id": session_id, "input": "q"}
    ).json()
    
    # Wait a bit for htop to exit
    time.sleep(1)
    
    # Check if htop has exited
    response = requests.get(f"{base_url}/sessions/{session_id}").json()
    if not response["running"]:
        print(f"htop exited with code: {response['exit_code']}")
    else:
        print("htop is still running, terminating session...")
        requests.delete(f"{base_url}/sessions/{session_id}")


if __name__ == "__main__":
    main()
