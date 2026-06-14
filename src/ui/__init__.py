"""
User Interface components for TOEIC Speaking Practice
- main_menu: Main menu interface for selecting test parts
- gui_app: Main GUI application for Part 1
- part2_gui: GUI application for Part 2 (Repeat)
- part3_gui: GUI application for Part 3 (Questions & Response)
- part4_gui: GUI application for Part 4 (Express Opinion)
- dictionary_popup: Dictionary lookup popup window
"""

from .main_menu import MainMenuApp
from .gui_app import TOEICGUIApp
from .part2_gui import Part2GUIApp
from .part3_gui import Part3GUIApp
from .part4_gui import Part4GUIApp
from .dictionary_popup import DictionaryPopup

__all__ = ["MainMenuApp", "TOEICGUIApp", "Part2GUIApp", "Part3GUIApp", "Part4GUIApp", "DictionaryPopup"]
