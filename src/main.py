"""
TOEIC Speaking Test - GUI Launcher
Main Menu Interface for selecting different TOEIC Speaking test parts

This script launches the GUI-based TOEIC Speaking Practice application
with a main menu to select different parts (1-5) or practice all.

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - tkinter (usually bundled with Python)
    - SpeechRecognition
    - pyaudio (for microphone input)

For Windows setup, see SETUP.md
"""

import sys
import tkinter as tk
from tkinter import messagebox

try:
    from src.ui.main_menu import MainMenuApp
    from src.ui.gui_app import TOEICGUIApp
    from src.ui.part2_gui import Part2GUIApp
except ImportError as e:
    error_msg = f"""
    Missing dependencies: {str(e)}
    
    Please install required packages first:
    
    pip install -r requirements.txt
    
    For detailed setup instructions, see docs/setup/SETUP.md
    """
    print(error_msg)
    sys.exit(1)


def main():
    """Main entry point - Launch the main menu"""
    print("\n" + "="*60)
    print("🎯 TOEIC SPEAKING PRACTICE - MAIN MENU")
    print("="*60)
    print("\n📝 Initializing application...")
    print("⏳ Please wait while the application loads...\n")
    
    try:
        # Create root window
        root = tk.Tk()
        
        # Create the main menu
        menu_app = MainMenuApp(root)
        
        # Register callback for Part 1
        def open_part1():
            """Open Part 1 interface"""
            # Close menu
            root.destroy()
            
            # Create new window for Part 1
            part1_root = tk.Tk()
            part1_app = TOEICGUIApp(part1_root)
            part1_root.mainloop()
        
        menu_app.register_part_callback(1, open_part1)
        
        # Register callback for Part 2
        def open_part2():
            """Open Part 2 interface"""
            # Close menu
            root.destroy()
            
            # Create new window for Part 2
            part2_root = tk.Tk()
            part2_app = Part2GUIApp(part2_root)
            part2_root.mainloop()
        
        menu_app.register_part_callback(2, open_part2)
        
        print("✓ Menu Application loaded successfully!")
        print("\n💡 Hướng dẫn:")
        print("  1. Chọn một phần (Part) để bắt đầu")
        print("  2. Hoặc chọn 'Thực hành toàn bộ' để luyện tập tất cả")
        print("  3. Part 1 & Part 2 sẵn sàng để sử dụng")
        print("  4. Các Part khác sắp ra mắt!\n")
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"""
        Error starting application: {str(e)}
        
        Please check:
        1. Microphone is connected and not in use
        2. All dependencies are installed
        3. Internet connection available (for LLM services)
        """
        print(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
