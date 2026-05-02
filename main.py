#!/usr/bin/env python3
"""
TOEIC Speaking Test - Root Entry Point
Wrapper that launches the application from src/main.py

Usage:
    python main.py

This wrapper ensures the application can be run from the root directory
while keeping the actual implementation organized in src/
"""

import sys
import os
from dotenv import load_dotenv

# Add current directory to path so we can import the src package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the actual main from src/
try:
    from src.main import main
except ImportError as e:
    error_msg = f"""
    Failed to import TOEIC Speaking application: {str(e)}
    
    Please ensure:
    1. All files are in correct locations (src/, tests/, docs/ folders exist)
    2. All dependencies are installed: pip install -r requirements.txt
    3. For detailed setup, see docs/setup/SETUP.md
    """
    print(error_msg)
    sys.exit(1)


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()
