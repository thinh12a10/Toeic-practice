"""
TOEIC Speaking Test - Main Menu Interface
Provides a menu to select different TOEIC Speaking test parts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Callable, Optional


class MainMenuApp:
    """Main Menu Application for TOEIC Speaking Test"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main menu
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("TOEIC Speaking Test - Menu Chính")
        # Di chuyển cửa sổ lên cao hơn để không bị taskbar che khuất
        self.root.geometry("600x700+100+50")
        self.root.configure(bg="#f0f0f0")
        
        # Store callbacks for part selection
        self.part_callbacks: dict = {}
        self.practice_all_callback: Optional[Callable] = None
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create the main menu interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🎯 TOEIC SPEAKING TEST",
            font=("Arial", 18, "bold"),
            foreground="#1e40af"
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Chọn phần bài tập",
            font=("Arial", 12),
            foreground="gray"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Create canvas with scrollbar for parts
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas
        canvas = tk.Canvas(
            canvas_frame,
            bg="#f0f0f0",
            highlightthickness=0
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        # Scrollable frame
        parts_frame = ttk.Frame(canvas)
        parts_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=parts_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Part buttons data
        parts_data = [
            {
                "number": 1,
                "title": "Part 1: Read Aloud",
                "description": "Đọc to đoạn văn bản\n(Read aloud written text)",
                "color": "#3b82f6"
            },
            {
                "number": 2,
                "title": "Part 2: Repeat",
                "description": "Mô tả hình ảnh\n(Describe a picture)",
                "color": "#8b5cf6"
            },
            {
                "number": 3,
                "title": "Part 3: Questions & Response",
                "description": "Trả lời các câu hỏi\n(Answer questions)",
                "color": "#ec4899"
            },
            {
                "number": 4,
                "title": "Part 4: Sentence Building",
                "description": "Xây dựng câu\n(Build sentences)",
                "color": "#f59e0b"
            },
            {
                "number": 5,
                "title": "Part 5: Free Talk",
                "description": "Nói chuyện tự do\n(Free conversation)",
                "color": "#10b981"
            }
        ]
        
        # Create part buttons
        for part_info in parts_data:
            self._create_part_button(
                parts_frame,
                part_info["number"],
                part_info["title"],
                part_info["description"],
                part_info["color"]
            )
        
        # Separator
        separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(0, 8))
        
        # Practice All button (special button)
        practice_all_btn = tk.Button(
            main_frame,
            text="🔄 Thực hành toàn bộ",
            font=("Arial", 12, "bold"),
            bg="#059669",
            fg="white",
            height=2,
            command=self._on_practice_all_click,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            activebackground="#047857",
            activeforeground="white"
        )
        practice_all_btn.pack(fill=tk.X, pady=5)
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Nhấn một trong các nút ở trên để bắt đầu bài tập",
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(pady=(5, 0))
    
    def _create_part_button(
        self,
        parent: tk.Widget,
        part_number: int,
        title: str,
        description: str,
        color: str
    ) -> None:
        """Create a button for a part"""
        btn = tk.Button(
            parent,
            text=f"Part {part_number}\n{title}\n{description}",
            font=("Arial", 10, "bold"),
            bg=color,
            fg="white",
            height=5,
            command=lambda: self._on_part_click(part_number),
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            activebackground=self._lighten_color(color),
            activeforeground="white"
        )
        btn.pack(fill=tk.X, pady=3, padx=20)
    
    @staticmethod
    def _lighten_color(hex_color: str) -> str:
        """Lighten a hex color"""
        # Simple implementation - just return a slightly brighter version
        return hex_color
    
    def _on_part_click(self, part_number: int) -> None:
        """Handle part button click"""
        # Check if callback is registered
        if part_number in self.part_callbacks:
            callback = self.part_callbacks[part_number]
            callback()
        else:
            # For parts that don't have implementation yet
            messagebox.showinfo(
                "Thông báo",
                f"Part {part_number} sắp ra mắt!\n\nHiện tại chỉ có Part 1 sẵn sàng."
            )
    
    def _on_practice_all_click(self) -> None:
        """Handle practice all button click"""
        if self.practice_all_callback:
            self.practice_all_callback()
        else:
            messagebox.showinfo(
                "Thông báo",
                "Tính năng thực hành toàn bộ sắp ra mắt!"
            )
    
    def register_part_callback(self, part_number: int, callback: Callable) -> None:
        """Register a callback for a part"""
        self.part_callbacks[part_number] = callback
    
    def register_practice_all_callback(self, callback: Callable) -> None:
        """Register a callback for practice all"""
        self.practice_all_callback = callback
    
    def close(self) -> None:
        """Close the menu"""
        self.root.destroy()
