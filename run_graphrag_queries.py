#!/usr/bin/env python3
import json
import subprocess
import os
import sys
from pathlib import Path
import time

def run_graphrag_query(query, method, root_dir):
    """Run a GraphRAG query and return the response."""
    try:
        # Execute the GraphRAG query command
        cmd = ["graphrag", "query", "--root", root_dir, "--method", method, "--query", query]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Return the output as the response
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running query: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return f"Error: {e}"

def process_query_file(json_file, root_dir):
    """Process a single JSON query file and add GraphRAG responses."""
    print(f"Processing {json_file}...")
    
    # Load the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create a backup of the original file
    backup_file = f"{json_file}.bak"
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Keep track of how many queries were processed
    total_queries = len(data['queries'])
    processed = 0
    
    # Process each query
    for query_item in data['queries']:
        processed += 1
        query_text = query_item['query']
        print(f"\nProcessing query {processed}/{total_queries}: {query_text[:50]}...")
        
        # Run local search
        print("Running local search...")
        local_response = run_graphrag_query(query_text, "local", root_dir)
        
        # Run global search
        print("Running global search...")
        global_response = run_graphrag_query(query_text, "global", root_dir)
        
        # Add responses to the query item
        query_item['responses'].append({
            "mode": "graphrag_local",
            "answer": local_response
        })
        
        query_item['responses'].append({
            "mode": "graphrag_global",
            "answer": global_response
        })
        
        # Save after each query in case of interruption
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Completed query {processed}/{total_queries}")
        
        # Add a small delay to avoid hammering the system
        time.sleep(1)
    
    print(f"\nCompleted processing {json_file}")
    print(f"Original file backed up to {backup_file}")

def main():
    # Check if the root directory is provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python run_graphrag_queries.py <graphrag_root_dir> [query_files_dir]")
        print("Example: python run_graphrag_queries.py ./myproject ./queries")
        sys.exit(1)
    
    # Get the GraphRAG root directory
    root_dir = sys.argv[1]
    
    # Get the directory containing query files
    queries_dir = sys.argv[2] if len(sys.argv) > 2 else "./queries"
    
    # Find all JSON files in the queries directory
    query_files = list(Path(queries_dir).glob("*.json"))
    
    if not query_files:
        print(f"No JSON files found in {queries_dir}")
        sys.exit(1)
    
    print(f"Found {len(query_files)} JSON files in {queries_dir}")
    
    # Process each file
    for json_file in query_files:
        process_query_file(str(json_file), root_dir)
    
    print("\nAll query files processed successfully!")

if __name__ == "__main__":
    main()
