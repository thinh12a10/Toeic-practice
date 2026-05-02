"""
Dictionary Popup UI for TOEIC Speaking Test
Displays word information with IPA, Vietnamese meaning, and audio pronunciation
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable
import threading
import pyttsx3


class DictionaryPopup:
    """
    Popup window for displaying word information
    Includes:
    - Word with IPA pronunciation
    - Definition
    - Vietnamese meaning
    - Speak button for audio pronunciation
    """
    
    def __init__(self, parent: tk.Widget, word_info: Dict[str, Any], 
                 on_close: Optional[Callable] = None):
        """
        Initialize DictionaryPopup
        
        Args:
            parent: Parent widget
            word_info: Dictionary with word information
            on_close: Callback when popup closes
        """
        self.parent = parent
        self.word_info = word_info
        self.on_close_callback = on_close
        self.tts_engine = None
        self._initialize_tts()
        
        # Create popup window
        self.popup = tk.Toplevel(parent)
        self.popup.title(f"Dictionary: {word_info.get('word', 'Word')}")
        self.popup.geometry("450x550")
        self.popup.resizable(True, True)
        self.popup.configure(bg="#f8f9fa")
        
        # Center on parent window
        self._center_on_parent()
        
        # Handle close event
        self.popup.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create UI
        self._create_ui()
    
    def _initialize_tts(self) -> None:
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Adjust speech rate
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            print(f"TTS initialization error: {e}")
            self.tts_engine = None
    
    def _center_on_parent(self) -> None:
        """Center popup on parent window"""
        try:
            self.popup.update_idletasks()
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            popup_width = self.popup.winfo_width()
            popup_height = self.popup.winfo_height()
            
            x = parent_x + (parent_width - popup_width) // 2
            y = parent_y + (parent_height - popup_height) // 2
            
            self.popup.geometry(f"+{x}+{y}")
        except:
            pass
    
    def _create_ui(self) -> None:
        """Create the popup UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.popup, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        
        # ======== WORD & IPA SECTION ========
        word_frame = ttk.LabelFrame(
            main_frame,
            text="Word & Pronunciation",
            padding=10
        )
        word_frame.pack(fill=tk.X, pady=(0, 10))
        word_frame.columnconfigure(1, weight=1)
        
        # Word title
        word_label = ttk.Label(
            word_frame,
            text=self.word_info.get('word', 'Word').upper(),
            font=("Arial", 20, "bold"),
            foreground="#1a5f7a"
        )
        word_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        
        # IPA
        ipa_title = ttk.Label(word_frame, text="IPA:", font=("Arial", 9, "bold"))
        ipa_title.grid(row=1, column=0, sticky=tk.NE, padx=(0, 5), pady=5)
        
        ipa_text = ttk.Label(
            word_frame,
            text=self.word_info.get('ipa', 'N/A'),
            font=("Courier", 12, "bold"),
            foreground="#d32f2f",
            wraplength=300
        )
        ipa_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Pronunciation description
        pron_title = ttk.Label(word_frame, text="Pronunciation:", font=("Arial", 9, "bold"))
        pron_title.grid(row=2, column=0, sticky=tk.NE, padx=(0, 5), pady=5)
        
        pron_text = ttk.Label(
            word_frame,
            text=self.word_info.get('pronunciation', 'N/A'),
            font=("Arial", 10),
            wraplength=300,
            justify=tk.LEFT
        )
        pron_text.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Speak button
        speak_button = tk.Button(
            word_frame,
            text="🔊 Speak",
            command=self._speak_word,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.RAISED,
            cursor="hand2"
        )
        speak_button.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # ======== DEFINITION SECTION ========
        def_frame = ttk.LabelFrame(
            main_frame,
            text="Definition",
            padding=10
        )
        def_frame.pack(fill=tk.X, pady=(0, 10))
        
        def_text = tk.Text(
            def_frame,
            height=3,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="white",
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        def_text.pack(fill=tk.BOTH, expand=True)
        def_text.insert("1.0", self.word_info.get('definition', 'No definition available'))
        def_text.config(state=tk.DISABLED)
        
        # Part of speech
        pos_text = self.word_info.get('part_of_speech', 'unknown')
        pos_label = ttk.Label(
            def_frame,
            text=f"Part of Speech: {pos_text}",
            font=("Arial", 9, "italic"),
            foreground="gray"
        )
        pos_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ======== VIETNAMESE MEANING ========
        viet_frame = ttk.LabelFrame(
            main_frame,
            text="Vietnamese Meaning (Nghĩa Tiếng Việt)",
            padding=10
        )
        viet_frame.pack(fill=tk.X, pady=(0, 10))
        
        viet_text = tk.Text(
            viet_frame,
            height=2,
            font=("Arial", 11, "bold"),
            wrap=tk.WORD,
            bg="#fff3e0",
            fg="#d84315",
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        viet_text.pack(fill=tk.BOTH, expand=True)
        viet_text.insert("1.0", self.word_info.get('vietnamese_meaning', 'Không có'))
        viet_text.config(state=tk.DISABLED)
        
        # ======== EXAMPLE SECTION ========
        example_frame = ttk.LabelFrame(
            main_frame,
            text="Example",
            padding=10
        )
        example_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        example_text = tk.Text(
            example_frame,
            height=2,
            font=("Arial", 9, "italic"),
            wrap=tk.WORD,
            bg="#e8f5e9",
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        example_text.pack(fill=tk.BOTH, expand=True)
        example_text.insert("1.0", self.word_info.get('example', 'No example available'))
        example_text.config(state=tk.DISABLED)
        
        # ======== BUTTONS ========
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=self._on_close,
            font=("Arial", 10),
            bg="#757575",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.RAISED,
            cursor="hand2"
        )
        close_button.pack(side=tk.RIGHT)
    
    def _speak_word(self) -> None:
        """Speak the word aloud using TTS"""
        if not self.tts_engine:
            print("TTS engine not available")
            return
        
        word = self.word_info.get('word', '')
        if not word:
            return
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._speak_thread, args=(word,), daemon=True)
        thread.start()
    
    def _speak_thread(self, word: str) -> None:
        """Thread function for speaking"""
        try:
            self.tts_engine.say(word)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error speaking word: {e}")
    
    def _on_close(self) -> None:
        """Handle popup close"""
        if self.on_close_callback:
            self.on_close_callback()
        self.popup.destroy()
    
    def show(self) -> None:
        """Show the popup (brings to front)"""
        self.popup.lift()
        self.popup.attributes('-topmost', True)
        self.popup.after(200, self.popup.attributes, '-topmost', False)
