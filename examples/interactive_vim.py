#!/usr/bin/env python3
"""Example of interactive vim usage with the Terminal MCP Server."""

import argparse
import sys
import time

import requests


def main():
    """Run the interactive vim example."""
    parser = argparse.ArgumentParser(description="Interactive Vim Example")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--file", type=str, default="/tmp/vim_test.txt", help="File to edit with vim"
    )
    parser.add_argument(
        "--emulator", type=str, default="xterm", 
        choices=["xterm", "gnome-terminal", "konsole", "tmux"],
        help="Terminal emulator to use"
    )
    
    args = parser.parse_args()
    
    # Start vim in a terminal emulator
    print(f"Starting vim to edit {args.file}...")
    response = requests.post(
        f"{args.url}/run",
        json={
            "command": f"vim {args.file}", 
            "timeout": 60,
            "use_terminal_emulator": True,
            "terminal_emulator": args.emulator
        }
    ).json()
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print("vim should now be running in a separate terminal window")
    
    # Wait for vim to initialize
    time.sleep(2)
    
    # Enter insert mode
    print("Entering insert mode (i)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "i"}
    )
    time.sleep(0.5)
    
    # Type some text
    text = "This is a test file created with vim through the Terminal MCP Server.\n\nIt demonstrates how AI agents can interact with terminal-based applications."
    print(f"Typing text: {text[:30]}...")
    
    # Send text in smaller chunks to avoid issues
    for chunk in [text[i:i+20] for i in range(0, len(text), 20)]:
        requests.post(
            f"{args.url}/send_input",
            json={"session_id": session_id, "input": chunk}
        )
        time.sleep(0.2)
    
    # Exit insert mode
    print("Exiting insert mode (Escape)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "\x1b"}
    )
    time.sleep(0.5)
    
    # Save and quit
    print("Saving and quitting (:wq)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": ":"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "w"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "q"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "\r"}
    )
    
    # Wait for vim to exit
    time.sleep(2)
    
    # Check if vim has exited
    response = requests.get(f"{args.url}/sessions/{session_id}").json()
    if not response["running"]:
        print(f"vim exited with code: {response['exit_code']}")
    else:
        print("vim is still running, terminating session...")
        requests.delete(f"{args.url}/sessions/{session_id}")
    
    # Check if the file was created
    try:
        with open(args.file, "r") as f:
            content = f.read()
        print(f"\nFile content:\n{content}")
    except FileNotFoundError:
        print(f"\nFile {args.file} was not created")


if __name__ == "__main__":
    main()
