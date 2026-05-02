"""
TOEIC Speaking Test - GUI Application with Audio Recording
Part 1: Read Aloud Task
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import pyaudio
import wave
import io
import re

from src.agents.speaking_agent import TOEICSpeakingAgent, UserProfile, Response
from src.core.part1_questions import Part1QuestionEngine
from src.agents.evaluator_agent import ResponseEvaluator
from src.core.feedback import FeedbackGenerator
from src.agents.dictionary_agent import DictionaryAgent
from src.ui.dictionary_popup import DictionaryPopup


class TOEICGUIApp:
    """GUI Application for TOEIC Speaking Test - Part 1"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("TOEIC Speaking Test - Part 1: Read Aloud")
        self.root.geometry("1200x850")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize components
        self.user_profile = UserProfile(
            user_id=str(uuid.uuid4())[:8],
            name="Test User",
            level="beginner"
        )
        self.agent = TOEICSpeakingAgent(self.user_profile)
        self.question_engine = Part1QuestionEngine(level=self.user_profile.level)
        self.evaluator = ResponseEvaluator()
        self.feedback_generator = FeedbackGenerator()
        self.dictionary_agent = DictionaryAgent()  # Initialize Dictionary Agent
        
        # State variables
        self.current_question: Optional[Dict[str, Any]] = None
        self.user_response_text: str = ""
        self.is_recording = False
        self.audio_data = None
        self.audio_frames = []  # For manual continuous recording
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Dictionary tracking
        self.clickable_words: Dict[str, Dict[str, Any]] = {}  # word -> word_info
        self.word_tags: Dict[str, str] = {}  # word -> tag_name for display
        
        # Session tracking
        self.session = None
        self.question_count = 0
        
        # Create UI
        self._create_ui()
        self._start_new_session()
        self._load_question()
    
    def _create_ui(self) -> None:
        """Create the user interface"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 1: Read Aloud",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # Level and session info
        info_label = ttk.Label(
            header_frame,
            text=f"Level: {self.user_profile.level.upper()} | User: {self.user_profile.name}",
            font=("Arial", 10),
            foreground="gray"
        )
        info_label.pack()
        
        # Status frame (top)
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to record. Click the microphone button to start.",
            font=("Arial", 10),
            foreground="green"
        )
        self.status_label.pack(anchor=tk.W)
        
        # Main content frame with two columns
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # =============== LEFT SIDE - TEXT DISPLAY ===============
        left_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        
        question_label = ttk.Label(
            left_frame,
            text="Read the following text aloud:",
            font=("Arial", 11, "bold")
        )
        question_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Instructions
        instruction_label = ttk.Label(
            left_frame,
            text="⏱️ Speaking time: 45 seconds",
            font=("Arial", 9),
            foreground="blue"
        )
        instruction_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Text to read
        text_scroll_frame = ttk.Frame(left_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.question_text = tk.Text(
            text_scroll_frame,
            font=("Arial", 13),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.question_text.pack(fill=tk.BOTH, expand=True)
        self.question_text.config(state=tk.DISABLED)  # Start disabled
        
        # Configure tags for word highlighting and links
        self.question_text.tag_config("clickable_word", foreground="blue", underline=True)
        self.question_text.tag_config("hover_word", background="#e3f2fd")
        
        # Bind mouse events for dictionary interaction
        self.question_text.bind("<Button-1>", self._on_text_click)
        self.question_text.bind("<Motion>", self._on_text_motion)
        self.question_text.bind("<Leave>", self._on_text_leave)
        
        # =============== RIGHT SIDE - FEEDBACK DISPLAY ===============
        right_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.rowconfigure(1, weight=1)
        
        feedback_label = ttk.Label(
            right_frame,
            text="Feedback & Results:",
            font=("Arial", 11, "bold")
        )
        feedback_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Feedback text with scrollbar
        feedback_scroll_frame = ttk.Frame(right_frame)
        feedback_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(feedback_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            feedback_scroll_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="#fffacd",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)
        scrollbar.config(command=self.results_text.yview)
        
        # Controls frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Microphone button (main control)
        self.mic_button = tk.Button(
            controls_frame,
            text="🎤 Start Recording",
            command=self._start_recording,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button (hidden until recording)
        self.stop_button = tk.Button(
            controls_frame,
            text="⏹️ Stop Recording",
            command=self._stop_recording,
            font=("Arial", 11, "bold"),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        # Hidden initially
        
        # Next question button
        self.next_button = tk.Button(
            controls_frame,
            text="➡️ Next Question",
            command=self._next_question,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        
        # Reset button
        self.reset_button = tk.Button(
            controls_frame,
            text="🔄 Reset",
            command=self._reset,
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
    
    def _start_new_session(self) -> None:
        """Start a new practice session"""
        self.session = self.agent.start_session()
        self.question_count = 0
        self.update_status("Session started. Ready for question 1.", "green")
    
    def _load_question(self) -> None:
        """Load a new Part 1 (Read Aloud) question asynchronously"""
        self.question_count += 1
        
        # Show loading message immediately
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert(tk.END, "⏳ Loading new question...\n\nPlease wait while the question is being prepared.")
        self.question_text.config(state=tk.DISABLED)
        
        self.update_status(f"Loading question {self.question_count}...", "blue")
        
        # Disable controls while loading
        self.mic_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        
        # Load question in background thread
        loading_thread = threading.Thread(target=self._load_question_background)
        loading_thread.daemon = True
        loading_thread.start()
    
    def _load_question_background(self) -> None:
        """Load question in background thread to prevent UI freezing"""
        try:
            # Generate a read_aloud question (may take time for LLM generation)
            self.current_question = self.question_engine.generate_question()
            
            # Update UI from main thread
            self.root.after(0, self._update_question_display)
        
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Error loading question: {str(e)}", "red"))
            self.root.after(0, self._enable_controls)
    
    def _update_question_display(self) -> None:
        """Update the question display (called from main thread via after)"""
        # Update question display
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert(tk.END, self.current_question.get("text", ""))
        
        # Apply word tags for dictionary lookup (must be done with text enabled)
        self._apply_word_tags()
        
        self.question_text.config(state=tk.DISABLED)
        
        # Reset UI state
        self.user_response_text = ""
        self.update_status(f"Question {self.question_count} loaded. Click words to see definitions. Click the microphone to record.", "blue")
        
        # Ensure recording controls are visible
        if self.stop_button.winfo_manager():
            self.stop_button.pack_forget()
        if not self.mic_button.winfo_manager():
            self.mic_button.pack(side=tk.LEFT, padx=5)
        if self.next_button.winfo_manager():
            self.next_button.pack_forget()
        
        # Re-enable controls
        self._enable_controls()
    
    def _enable_controls(self) -> None:
        """Re-enable control buttons after question is loaded"""
        self.mic_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
    
    def _start_recording(self) -> None:
        """Start recording audio from microphone"""
        self.is_recording = True
        self.update_status("🔴 Recording... Read aloud and press STOP button when finished (max 60 seconds).", "red")
        
        # Update button state
        self.mic_button.pack_forget()
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
    
    def _show_recording_controls(self) -> None:
        """Ensure recording controls are visible"""
        if self.stop_button.winfo_manager():
            self.stop_button.pack_forget()
        if not self.mic_button.winfo_manager():
            self.mic_button.pack(side=tk.LEFT, padx=5)
    
    def _record_audio(self) -> None:
        """Record audio continuously until stop button is pressed"""
        try:
            # Audio recording parameters
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000  # 16kHz sampling rate
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Open audio stream
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            self.audio_frames = []
            
            # Record continuously until stop button is pressed
            while self.is_recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except Exception as e:
                    print(f"⚠ Recording error: {e}")
                    break
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Process the recorded audio
            if self.audio_frames:
                self._process_recorded_audio()
        
        except Exception as e:
            self.update_status(f"❌ Recording error: {str(e)}", "red")
        finally:
            self.is_recording = False
            self.root.after(0, self._stop_recording)
    
    def _process_recorded_audio(self) -> None:
        """Convert recorded audio frames to text"""
        try:
            self.update_status("🔄 Processing speech...", "blue")
            
            # Audio parameters (must match recording)
            CHANNELS = 1
            RATE = 16000
            
            # Convert audio frames to bytes
            audio_bytes = b''.join(self.audio_frames)
            
            # Create AudioData object for speech recognition
            audio = sr.AudioData(audio_bytes, RATE, 2)  # 2 bytes per sample (16-bit)
            
            # Use Google Speech Recognition API
            text = self.recognizer.recognize_google(audio)
            self.user_response_text = text
            
            # Evaluate the response
            self.root.after(0, self._evaluate_response)
        
        except sr.UnknownValueError:
            self.update_status("❌ Could not understand audio. Please speak more clearly.", "red")
        except sr.RequestError as e:
            self.update_status(f"❌ Service error: {str(e)}", "red")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", "red")
    
    def _stop_recording(self) -> None:
        """Stop recording and process the audio"""
        self.is_recording = False
        self.stop_button.pack_forget()
        self.mic_button.pack(side=tk.LEFT, padx=5)
        self.update_status("⏸️ Recording stopped. Processing your speech...", "blue")
    
    def _evaluate_response(self) -> None:
        """Evaluate the recorded and transcribed response"""
        try:
            # Score the response
            score = self.evaluator.evaluate(
                self.user_response_text,
                self.current_question,
                self.user_profile.level
            )
            
            # Generate feedback
            feedback = self.feedback_generator.generate_feedback(
                self.user_response_text,
                self.current_question,
                score
            )
            
            # Store response in session
            response = Response(
                question_id=self.current_question.get("id", "unknown"),
                user_text=self.user_response_text,
                score=score,
                feedback=feedback
            )
            self.session.add_response(response)
            
            # Display results
            self._show_results(score, feedback)
        
        except Exception as e:
            self.update_status(f"❌ Evaluation error: {str(e)}", "red")
    
    def _show_results(self, score: float, feedback: str) -> None:
        """
        Display evaluation results and feedback
        
        Args:
            score: Score from evaluator
            feedback: Feedback text
        """
        # Format and display results
        results_content = f"""
📊 YOUR SCORE: {score:.1f}/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Your Response:
{self.user_response_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Feedback:
{feedback}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, results_content)
        self.results_text.config(state=tk.DISABLED)
        
        # Show next and reset buttons
        if not self.next_button.winfo_manager():
            self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.update_status("✅ Evaluation complete! Click 'Next Question' to continue.", "green")
    
    def _next_question(self) -> None:
        """Load the next question"""
        self._load_question()
    
    def _reset(self) -> None:
        """
        Reset - generate new question and clear feedback
        """
        # Clear feedback
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        # Hide next button
        if self.next_button.winfo_manager():
            self.next_button.pack_forget()
        
        # Load new question
        self._load_question()
    
    def update_status(self, message: str, color: str = "black") -> None:
        """
        Update status label
        
        Args:
            message: Status message
            color: Text color
        """
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    # ============ DICTIONARY FEATURE METHODS ============
    
    def _apply_word_tags(self) -> None:
        """Apply clickable tags to words in the question text"""
        if not self.current_question:
            return
        
        text_content = self.question_text.get("1.0", tk.END).strip()
        if not text_content:
            return
        
        # Extract words suitable for dictionary
        words = self.dictionary_agent.extract_words_from_text(text_content)
        self.clickable_words = {}
        
        # Apply tags to each word
        self.question_text.config(state=tk.NORMAL)
        for word in words:
            # Find all occurrences of the word (case-insensitive)
            search_pattern = f"\\b{word}\\b"
            start_pos = "1.0"
            
            for occurrence in range(100):  # Search up to 100 occurrences
                pos = self.question_text.search(
                    search_pattern,
                    start_pos,
                    nocase=True,
                    regexp=True
                )
                
                if not pos:
                    break
                
                # Calculate end position
                end_pos = f"{pos}+{len(word)}c"
                
                # Apply clickable tag
                self.question_text.tag_add("clickable_word", pos, end_pos)
                
                # Store word info reference
                word_key = f"{pos}:{end_pos}"
                self.word_tags[word_key] = word
                
                # Move start position for next search
                start_pos = end_pos
        
        self.question_text.config(state=tk.DISABLED)
    
    def _on_text_click(self, event: tk.Event) -> None:
        """Handle text click - show dictionary popup for clicked word"""
        # Get position of click
        pos = self.question_text.index(f"@{event.x},{event.y}")
        
        # Get the word at this position
        word = self._get_word_at_position(pos)
        
        if not word or len(word) < 3:
            return
        
        # Show loading message
        self.update_status(f"📚 Fetching definition for '{word}'...", "blue")
        
        # Fetch word info in background
        thread = threading.Thread(
            target=self._fetch_word_info_async,
            args=(word,),
            daemon=True
        )
        thread.start()
    
    def _on_text_motion(self, event: tk.Event) -> None:
        """Handle mouse motion - highlight words on hover"""
        pos = self.question_text.index(f"@{event.x},{event.y}")
        word = self._get_word_at_position(pos)
        
        # Remove all hover tags first
        self.question_text.tag_remove("hover_word", "1.0", tk.END)
        
        # Apply hover tag if over a clickable word
        if word and len(word) >= 3:
            # Find and highlight this word occurrence
            word_start = f"{pos} wordstart"
            word_end = f"{pos} wordend"
            self.question_text.tag_add("hover_word", word_start, word_end)
            self.root.config(cursor="hand2")
        else:
            self.root.config(cursor="arrow")
    
    def _on_text_leave(self, event: tk.Event) -> None:
        """Handle mouse leaving text area - remove hover highlight"""
        self.question_text.tag_remove("hover_word", "1.0", tk.END)
        self.root.config(cursor="arrow")
    
    def _get_word_at_position(self, pos: str) -> Optional[str]:
        """Get the word at the given position in text widget"""
        try:
            word_start = f"{pos} wordstart"
            word_end = f"{pos} wordend"
            word = self.question_text.get(word_start, word_end).strip()
            
            # Remove punctuation
            import string
            word = word.strip(string.punctuation)
            
            return word if word and len(word) >= 3 else None
        except:
            return None
    
    def _fetch_word_info_async(self, word: str) -> None:
        """Fetch word information in background thread"""
        try:
            word_info = self.dictionary_agent.get_word_info(word)
            self.root.after(0, lambda: self._show_dictionary_popup(word_info))
        except Exception as e:
            print(f"Error fetching word info: {e}")
            self.root.after(0, lambda: self.update_status(f"❌ Error fetching word info", "red"))
    
    def _show_dictionary_popup(self, word_info: Dict[str, Any]) -> None:
        """Display dictionary popup with word information"""
        try:
            popup = DictionaryPopup(
                self.root,
                word_info,
                on_close=lambda: self.update_status("Ready to continue", "green")
            )
            popup.show()
            self.update_status(f"📖 Showing dictionary entry for '{word_info.get('word', 'word')}'", "green")
        except Exception as e:
            print(f"Error showing popup: {e}")
            self.update_status("❌ Error displaying dictionary popup", "red")


def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = TOEICGUIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
