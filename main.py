"""
Redshift Agentic AI — POC Entry Point
 
Run this file to:
1. Initialize the sample SQLite database
2. Start the interactive agent CLI
 
Usage:
    python main.py
"""
 
from agent.database import setup_sample_database
from agent.agent import run_interactive
import os
 
 
def main():
    # Step 1: Set up database if it doesn't exist
    if not os.path.exists("poc_database.db"):
        print("Setting up sample database...")
        setup_sample_database()
        print("Done!\n")
 
    # Step 2: Run the interactive agent
    run_interactive()
 
 
if __name__ == "__main__":
    main()