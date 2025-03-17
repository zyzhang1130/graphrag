#!/bin/bash

# Make the Python script executable
chmod +x run_graphrag_queries.py

# Run the Python script with the GraphRAG root directory and queries directory
python run_graphrag_queries.py ./myproject ./queries
