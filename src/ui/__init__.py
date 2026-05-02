"""
User Interface components for TOEIC Speaking Practice
- main_menu: Main menu interface for selecting test parts
- gui_app: Main GUI application for Part 1
- part2_gui: GUI application for Part 2 (Repeat)
- dictionary_popup: Dictionary lookup popup window
"""

from .main_menu import MainMenuApp
from .gui_app import TOEICGUIApp
from .part2_gui import Part2GUIApp
from .dictionary_popup import DictionaryPopup

__all__ = ["MainMenuApp", "TOEICGUIApp", "Part2GUIApp", "DictionaryPopup"]
