#!/usr/bin/env python3
"""
Test the EXACT workflow Amazon Q needs
"""
import json
import subprocess
import time

def send_mcp_request(server, request):
    """Send MCP request and get response"""
    server.stdin.write(json.dumps(request) + "\n")
    server.stdin.flush()
    response = json.loads(server.stdout.readline())
    return response

def test_full_vim_workflow():
    """Test: Open terminal -> vim -> write 'Dumb dumb dumber' -> save -> cat file"""
    print("=== Testing Full Vim Workflow ===")
    
    server = subprocess.Popen(
        ["python3", "mcp_server_standalone.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        time.sleep(1)
        
        # 1. Start shell
        print("1. Starting shell...")
        start_req = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "start_shell", "arguments": {}}
        }
        resp = send_mcp_request(server, start_req)
        session_id = resp["result"]["content"][0]["text"].split("Session ID: ")[1].split("\n")[0]
        print(f"   ✓ Shell started: {session_id}")
        time.sleep(2)
        
        # 2. Open vim to create new file
        print("2. Opening vim with file 'testfile.txt'...")
        vim_req = {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "vim testfile.txt\\r"}}
        }
        resp = send_mcp_request(server, vim_req)
        print("   ✓ Vim command sent")
        time.sleep(2)
        
        # 3. Enter insert mode
        print("3. Entering insert mode (press 'i')...")
        insert_req = {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "i"}}
        }
        resp = send_mcp_request(server, insert_req)
        print("   ✓ Insert mode activated")
        time.sleep(0.5)
        
        # 4. Type the text
        print("4. Typing 'Dumb dumb dumber'...")
        type_req = {
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "Dumb dumb dumber"}}
        }
        resp = send_mcp_request(server, type_req)
        print("   ✓ Text typed")
        time.sleep(0.5)
        
        # 5. Exit insert mode (Escape)
        print("5. Exiting insert mode (Escape)...")
        escape_req = {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call", 
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "\\x1b"}}
        }
        resp = send_mcp_request(server, escape_req)
        print("   ✓ Escaped insert mode")
        time.sleep(0.5)
        
        # 6. Save and quit (:wq)
        print("6. Saving and quitting (:wq)...")
        save_req = {
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": ":wq"}}
        }
        resp = send_mcp_request(server, save_req)
        time.sleep(0.5)
        
        # 7. Press Enter to execute save command
        print("7. Pressing Enter...")
        enter_req = {
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "\\r"}}
        }
        resp = send_mcp_request(server, enter_req)
        print("   ✓ File saved and vim exited")
        time.sleep(2)
        
        # 8. Cat the file to verify content
        print("8. Displaying file content with 'cat testfile.txt'...")
        cat_req = {
            "jsonrpc": "2.0", "id": 8, "method": "tools/call",
            "params": {"name": "send_input", "arguments": {"session_id": session_id, "input": "cat testfile.txt\\r"}}
        }
        resp = send_mcp_request(server, cat_req)
        time.sleep(1)
        
        # 9. Get final output to see everything
        print("9. Getting final terminal output...")
        output_req = {
            "jsonrpc": "2.0", "id": 9, "method": "tools/call",
            "params": {"name": "get_output", "arguments": {"session_id": session_id}}
        }
        resp = send_mcp_request(server, output_req)
        
        final_output = resp["result"]["content"][0]["text"]
        
        print("\n" + "="*70)
        print("FINAL TERMINAL OUTPUT:")
        print("="*70)
        print(final_output[-1000:])  # Show last 1000 chars
        print("="*70)
        
        # Check if workflow succeeded
        if "Dumb dumb dumber" in final_output:
            print("\n🎉 SUCCESS! Full workflow completed:")
            print("   ✓ Opened vim")
            print("   ✓ Wrote text in insert mode") 
            print("   ✓ Saved file with escape + :wq")
            print("   ✓ File content verified with cat")
            print("   ✓ Text 'Dumb dumb dumber' confirmed in output")
            
            # Clean up test file
            import os
            if os.path.exists("testfile.txt"):
                os.remove("testfile.txt")
                print("   ✓ Test file cleaned up")
            
            return True
        else:
            print("❌ FAILED: Text 'Dumb dumb dumber' not found in output")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        server.terminate()

if __name__ == "__main__":
    success = test_full_vim_workflow()
    if success:
        print("\n🎉 Amazon Q will be able to use vim successfully!")
    else:
        print("\n❌ There are still issues to fix")