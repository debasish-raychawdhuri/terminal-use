#!/usr/bin/env python3
"""Debug ANSI sequence parsing to understand what's going wrong."""

import re

def analyze_ansi_sequences(text):
    """Analyze all ANSI sequences in the text."""
    
    # Find all ANSI escape sequences
    ansi_pattern = re.compile(r'\x1b\[([0-9;?]*)([a-zA-Z])')
    
    sequences = []
    pos = 0
    
    for match in ansi_pattern.finditer(text):
        # Get text before this sequence
        before_text = text[pos:match.start()]
        
        params_str = match.group(1)
        command = match.group(2)
        full_seq = match.group(0)
        
        sequences.append({
            'position': match.start(),
            'before_text': before_text,
            'params': params_str,
            'command': command,
            'full_sequence': full_seq,
            'repr': repr(full_seq)
        })
        
        pos = match.end()
    
    # Get remaining text after last sequence
    remaining_text = text[pos:]
    
    return sequences, remaining_text

def main():
    # Read the calendar raw output
    with open('calendar_raw_output.txt', 'r') as f:
        raw_output = f.read()
    
    print("=== ANSI SEQUENCE ANALYSIS ===")
    print(f"Total length: {len(raw_output)} characters")
    
    sequences, remaining = analyze_ansi_sequences(raw_output)
    
    print(f"Found {len(sequences)} ANSI sequences")
    print(f"Remaining text after last sequence: {len(remaining)} chars")
    
    # Group sequences by command type
    by_command = {}
    for seq in sequences:
        cmd = seq['command']
        if cmd not in by_command:
            by_command[cmd] = []
        by_command[cmd].append(seq)
    
    print("\n=== SEQUENCES BY COMMAND TYPE ===")
    for cmd, seqs in by_command.items():
        print(f"{cmd}: {len(seqs)} sequences")
        # Show first few examples
        for seq in seqs[:3]:
            print(f"  {seq['repr']} (params: '{seq['params']}')")
        if len(seqs) > 3:
            print(f"  ... and {len(seqs) - 3} more")
    
    # Analyze the 'm' (SGR) sequences specifically
    print("\n=== SGR (COLOR/FORMATTING) SEQUENCES ===")
    sgr_sequences = by_command.get('m', [])
    
    unique_sgr = {}
    for seq in sgr_sequences:
        params = seq['params']
        if params not in unique_sgr:
            unique_sgr[params] = 0
        unique_sgr[params] += 1
    
    print("Unique SGR parameter combinations:")
    for params, count in sorted(unique_sgr.items()):
        print(f"  '{params}': {count} times")
    
    # Show the first 20 sequences with context
    print("\n=== FIRST 20 SEQUENCES WITH CONTEXT ===")
    for i, seq in enumerate(sequences[:20]):
        before = repr(seq['before_text'][-20:]) if len(seq['before_text']) > 20 else repr(seq['before_text'])
        print(f"{i+1:2d}. {before} → {seq['repr']}")

if __name__ == "__main__":
    main()
