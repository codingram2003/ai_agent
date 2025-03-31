#!/usr/bin/env python3
import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser(description='Process data and generate analysis')
    parser.add_argument('--input', help='Input data file path')
    parser.add_argument('--output', help='Output file path')
    args = parser.parse_args()
    
    # Load input data if provided
    data = {}
    if args.input and os.path.exists(args.input):
        with open(args.input, 'r') as f:
            data = json.load(f)
    
    # Process data (simple example)
    result = {
        "analysis": {
            "item_count": len(data) if isinstance(data, dict) else 0,
            "processed_timestamp": __import__('datetime').datetime.now().isoformat()
        }
    }
    
    # Add processed data
    if data:
        result["processed_data"] = data
    
    # Save output
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Also save to standard output_data.json for the agent to pick up
        output_dir = os.path.dirname(args.output)
        with open(os.path.join(output_dir, 'output_data.json'), 'w') as f:
            json.dump(result, f, indent=2)
    
    print(f"Data processed successfully. Items analyzed: {result['analysis']['item_count']}")
    return 0

if __name__ == "__main__":
    main()
