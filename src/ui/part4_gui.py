"""
TOEIC Speaking Test - GUI Application for Part 4
Part 4: Document-Based Question Answering (Questions 8, 9, 10)

Students have 45 seconds to read a document, then answer 3 questions:
- Question 8 (15s): Basic factual details
- Question 9 (15s): Specific details / confirmation
- Question 10 (30s): List multiple items
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
import pyaudio
import time
import wave
import io

from src.agents.speaking_agent import TOEICSpeakingAgent, UserProfile, Response
from src.core.part4_questions import Part4QuestionsEngine
from src.agents.gemini_part4_evaluator import GeminiPart4Evaluator
from src.core.feedback import FeedbackGenerator


class Part4GUIApp:
    """GUI Application for TOEIC Speaking Test - Part 4 (Document-Based Questions)"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application for Part 4
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("TOEIC Speaking Test - Part 4: Document Questions")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width * 0.9)
        height = int(screen_height * 0.85)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize components
        self.user_profile = UserProfile(
            user_id=str(uuid.uuid4())[:8],
            name="Test User",
            level="beginner"
        )
        self.agent = TOEICSpeakingAgent(self.user_profile)
        self.question_engine = Part4QuestionsEngine(level=self.user_profile.level)
        self.evaluator = GeminiPart4Evaluator()
        self.feedback_generator = FeedbackGenerator()
        
        # State variables
        self.current_document_set: Optional[Dict[str, Any]] = None
        self.current_question_index: int = 0  # 0=Q8, 1=Q9, 2=Q10
        self.user_responses: List[Dict[str, Any]] = [{}, {}, {}]  # For 3 questions
        self.question_evaluations: List[Dict[str, Any]] = []
        self.is_recording = False
        self.audio_frames = []
        self.audio_bytes: bytes = b''
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_loading = False
        
        # Timer state
        self.prep_time_remaining = 0
        self.speaking_time_remaining = 0
        self.in_prep_phase = False
        self.in_speaking_phase = False
        
        # Session tracking
        self.session = None
        self.document_count = 0
        
        # Create UI
        self._create_ui()
        
        self.update_status("Initializing...", "blue")
        
        self._start_new_session()
        self._load_document()
    
    def _create_ui(self) -> None:
        """Create the user interface"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 4: Document Questions",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        info_label = ttk.Label(
            header_frame,
            text=f"Level: {self.user_profile.level.upper()} | User: {self.user_profile.name}",
            font=("Arial", 10),
            foreground="gray"
        )
        info_label.pack()
        
        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready. Read the document and prepare your answers.",
            font=("Arial", 10),
            foreground="green"
        )
        self.status_label.pack(anchor=tk.W)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # =============== LEFT SIDE - DOCUMENT & QUESTIONS ===============
        left_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(3, weight=1)
        
        # Document type label
        doctype_label = ttk.Label(
            left_frame,
            text="Document Type:",
            font=("Arial", 11, "bold")
        )
        doctype_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.doctype_display = ttk.Label(
            left_frame,
            text="",
            font=("Arial", 9),
            foreground="gray"
        )
        self.doctype_display.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        # Document display
        doc_scroll_frame = ttk.Frame(left_frame)
        doc_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        doc_scrollbar = ttk.Scrollbar(doc_scroll_frame)
        doc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.document_text = tk.Text(
            doc_scroll_frame,
            font=("Courier", 9),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            yscrollcommand=doc_scrollbar.set
        )
        self.document_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.document_text.config(state=tk.DISABLED)
        doc_scrollbar.config(command=self.document_text.yview)
        
        # Current question label
        q_label = ttk.Label(
            left_frame,
            text="Current Question:",
            font=("Arial", 11, "bold")
        )
        q_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Question display
        q_scroll_frame = ttk.Frame(left_frame)
        q_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        q_scrollbar = ttk.Scrollbar(q_scroll_frame)
        q_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.question_text = tk.Text(
            q_scroll_frame,
            font=("Arial", 10, "bold"),
            wrap=tk.WORD,
            bg="#e8f4f8",
            fg="#1a1a1a",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            yscrollcommand=q_scrollbar.set,
            height=4
        )
        self.question_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.question_text.config(state=tk.DISABLED)
        q_scrollbar.config(command=self.question_text.yview)
        
        # =============== RIGHT SIDE - INSTRUCTIONS & FEEDBACK ===============
        right_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.rowconfigure(1, weight=1)
        
        instr_label = ttk.Label(
            right_frame,
            text="Instructions & Results:",
            font=("Arial", 11, "bold")
        )
        instr_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        feedback_scroll_frame = ttk.Frame(right_frame)
        feedback_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(feedback_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            feedback_scroll_frame,
            font=("Arial", 9),
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
        
        self._display_instructions()
        
        # Controls frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Question counter
        self.question_counter = ttk.Label(
            controls_frame,
            text="Question: Preparation",
            font=("Arial", 10),
            foreground="blue"
        )
        self.question_counter.pack(side=tk.LEFT, padx=20)
        
        sep1 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep1.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Timers
        self.timer_label = ttk.Label(
            controls_frame,
            text="Time: --",
            font=("Arial", 10),
            foreground="blue"
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        sep2 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep2.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Microphone button
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
        
        # Stop button (initially hidden)
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
        
        # Next button
        self.next_button = tk.Button(
            controls_frame,
            text="➡️ Next",
            command=self._next_question,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
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
    
    def _display_instructions(self) -> None:
        """Display initial instructions"""
        instructions = """TOEIC SPEAKING PART 4 - INSTRUCTIONS

How this test works:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read the DOCUMENT carefully
   • You have 45 seconds preparation time
   • Analyze all the information

2. Answer THREE questions:
   
   QUESTION 8 (15 seconds)
   → Basic factual details (Who, What, Where, When)
   → Test your ability to find information quickly
   
   QUESTION 9 (15 seconds)  
   → Specific details or confirmation
   → Test your ability to verify accuracy
   
   QUESTION 10 (30 seconds)
   → List multiple related items
   → Test your ability to synthesize information

3. Recording:
   • Click "START RECORDING" when ready
   • Speak clearly and naturally
   • Answer with accuracy and completeness

4. Evaluation focuses on:
   ✓ Accuracy and completeness (40%)
   ✓ Fluency and clarity (30%)
   ✓ Grammar and vocabulary (30%)

Ready? Load a document to begin! ✓"""
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, instructions)
        self.results_text.config(state=tk.DISABLED)
    
    def update_status(self, message: str, color: str = "black") -> None:
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
    
    def _start_new_session(self) -> None:
        """Start a new practice session"""
        self.session = self.agent.start_session()
    
    def _load_document(self) -> None:
        """Load a new document"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.update_status("Loading document...", "blue")
        
        def load_in_thread():
            try:
                doc_set = self.question_engine.get_next_document()
                
                if not doc_set:
                    self.root.after(0, lambda: self.update_status(
                        "Failed to load document. Please try again.",
                        "red"
                    ))
                    return
                
                self.current_document_set = doc_set
                self.current_question_index = 0
                self.user_responses = [{}, {}, {}]
                self.question_evaluations = []
                self.document_count += 1
                
                self.root.after(0, self._display_document)
                self.root.after(0, lambda: self.update_status(
                    "Document loaded. You have 45 seconds to read it.",
                    "green"
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(
                    f"Error loading document: {str(e)}",
                    "red"
                ))
            finally:
                self.is_loading = False
        
        thread = threading.Thread(target=load_in_thread, daemon=True)
        thread.start()
    
    def _display_document(self) -> None:
        """Display the document"""
        if not self.current_document_set:
            return
        
        # Display document type
        doc_type = self.current_document_set.get("document_type", "Document")
        self.doctype_display.config(text=f"Type: {doc_type}")
        
        # Display document
        self.document_text.config(state=tk.NORMAL)
        self.document_text.delete(1.0, tk.END)
        document = self.current_document_set.get("document", "")
        self.document_text.insert(tk.END, document)
        self.document_text.config(state=tk.DISABLED)
        
        # Clear question display initially
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, "Reading document... Get ready!")
        self.question_text.config(state=tk.DISABLED)
        
        # Start preparation phase
        self._start_preparation()
    
    def _start_preparation(self) -> None:
        """Start the 45-second preparation phase"""
        self.in_prep_phase = True
        self.prep_time_remaining = 45
        self.question_counter.config(text="Phase: Preparation (45s)")
        self.update_status("Preparation phase: Read and analyze the document carefully.", "blue")
        self.mic_button.config(state=tk.DISABLED, bg="#CCCCCC")
        self.next_button.config(state=tk.DISABLED, bg="#CCCCCC")
        
        self._run_prep_timer()
    
    def _run_prep_timer(self) -> None:
        """Run the preparation timer"""
        if self.prep_time_remaining > 0:
            self.timer_label.config(text=f"Time: {self.prep_time_remaining}s")
            self.prep_time_remaining -= 1
            self.root.after(1000, self._run_prep_timer)
        else:
            self.timer_label.config(text="Time: 0s")
            self.in_prep_phase = False
            self._prepare_first_question()
    
    def _prepare_first_question(self) -> None:
        """Prepare for first question"""
        self.current_question_index = 0
        self._show_current_question()
    
    def _show_current_question(self) -> None:
        """Display the current question"""
        if self.current_question_index >= 3:
            self._show_all_results()
            return
        
        questions = self.current_document_set.get("questions", [])
        current_q = questions[self.current_question_index]
        
        q_num = current_q.get("number", 8 + self.current_question_index)
        q_text = current_q.get("text", "")
        q_time = current_q.get("time_limit", 15)
        
        # Display question
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, f"Question {q_num}:\n{q_text}")
        self.question_text.config(state=tk.DISABLED)
        
        # Update counter
        self.question_counter.config(text=f"Question: {q_num} ({q_time}s)")
        
        # Enable recording
        self.in_speaking_phase = True
        self.speaking_time_remaining = q_time
        self.mic_button.config(state=tk.NORMAL, bg="#4CAF50")
        self.update_status(f"Question {q_num}: Ready to record. Click the microphone button.", "green")
    
    def _start_recording(self) -> None:
        """Start recording"""
        self.is_recording = True
        
        current_q = self.current_document_set.get("questions", [])[self.current_question_index]
        q_time = current_q.get("time_limit", 15)
        q_num = current_q.get("number", 8 + self.current_question_index)
        
        self.update_status(f"🔴 Recording... Question {q_num} ({q_time} seconds max).", "red")
        
        self.mic_button.pack_forget()
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()
    
    def _record_audio(self) -> None:
        """Record audio"""
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            current_q = self.current_document_set.get("questions", [])[self.current_question_index]
            MAX_TIME = current_q.get("time_limit", 15)
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            self.audio_frames = []
            start_time = time.time()
            
            while self.is_recording:
                elapsed = time.time() - start_time
                if elapsed >= MAX_TIME:
                    self.is_recording = False
                    break
                
                remaining = int(MAX_TIME - elapsed)
                self.root.after(0, lambda r=remaining: self.timer_label.config(text=f"Time: {r}s"))
                
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except:
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if self.audio_frames:
                self._process_audio()
        
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Recording error: {str(e)}", "red"))
        finally:
            self.is_recording = False
            self.root.after(0, self._stop_recording)
    
    def _process_audio(self) -> None:
        """Process the recorded audio"""
        self.update_status("Processing response...", "blue")
        
        def process_in_thread():
            try:
                if not self.audio_frames:
                    self.root.after(0, lambda: self.update_status("No audio recorded.", "red"))
                    return
                
                # Create audio bytes
                audio_data = io.BytesIO()
                with wave.open(audio_data, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes(b''.join(self.audio_frames))
                
                audio_bytes = audio_data.getvalue()
                
                # Get current question and document
                questions = self.current_document_set.get("questions", [])
                current_q = questions[self.current_question_index]
                document = self.current_document_set.get("document", "")
                
                response_text = "[Audio response recorded]"
                
                # Evaluate
                evaluation = self.evaluator.evaluate(
                    audio_bytes=audio_bytes,
                    user_response=response_text,
                    document=document,
                    question=current_q,
                    user_level=self.user_profile.level
                )
                
                # Store response and evaluation
                self.user_responses[self.current_question_index] = {
                    "question": current_q,
                    "response": response_text,
                    "audio_bytes": audio_bytes
                }
                self.question_evaluations.append(evaluation)
                
                # Display feedback
                self.root.after(0, self._display_question_feedback, evaluation)
                
                # Enable next
                self.root.after(0, lambda: self.next_button.config(state=tk.NORMAL, bg="#2196F3"))
                self.root.after(0, lambda: self.update_status(
                    "Response recorded. Click 'Next' for the next question.",
                    "green"
                ))
            
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error: {str(e)}", "red"))
        
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()
    
    def _stop_recording(self) -> None:
        """Stop recording"""
        self.is_recording = False
        self.stop_button.pack_forget()
        self.mic_button.pack(side=tk.LEFT, padx=5)
        self.update_status("Recording stopped. Processing...", "blue")
    
    def _display_question_feedback(self, evaluation: Dict[str, Any]) -> None:
        """Display feedback for current question"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        q_num = 8 + self.current_question_index
        completeness = evaluation.get("completeness", {}).get("score", 0)
        fluency = evaluation.get("fluency", {}).get("score", 0)
        grammar = evaluation.get("grammar", {}).get("score", 0)
        total = evaluation.get("total_score", 0)
        
        feedback_text = f"""Question {q_num} - Evaluation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCORES:
  • Completeness & Accuracy: {completeness}/40
  • Fluency: {fluency}/30
  • Grammar & Vocabulary: {grammar}/30
  
  TOTAL: {total:.1f}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 FEEDBACK:

Completeness & Accuracy:
{evaluation.get("completeness", {}).get("feedback", "")}

Fluency:
{evaluation.get("fluency", {}).get("feedback", "")}

Grammar & Vocabulary:
{evaluation.get("grammar", {}).get("feedback", "")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click "Next" for Question {q_num + 1} or view final results"""
        
        self.results_text.insert(tk.END, feedback_text)
        self.results_text.config(state=tk.DISABLED)
    
    def _next_question(self) -> None:
        """Move to next question"""
        self.current_question_index += 1
        
        if self.current_question_index >= 3:
            self._show_all_results()
        else:
            self._show_current_question()
    
    def _show_all_results(self) -> None:
        """Show all results from the 3 questions"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Calculate overall stats
        total_scores = []
        completeness_scores = []
        fluency_scores = []
        grammar_scores = []
        
        for eval_data in self.question_evaluations:
            total_scores.append(eval_data.get("total_score", 0))
            completeness_scores.append(eval_data.get("completeness", {}).get("score", 0))
            fluency_scores.append(eval_data.get("fluency", {}).get("score", 0))
            grammar_scores.append(eval_data.get("grammar", {}).get("score", 0))
        
        avg_total = sum(total_scores) / len(total_scores) if total_scores else 0
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0
        
        # Build summary
        summary = f"""🎉 ALL QUESTIONS COMPLETE! ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 OVERALL RESULTS (Average Scores):
  • TOTAL SCORE: {avg_total:.1f}/100
  • Completeness & Accuracy: {avg_completeness:.1f}/40
  • Fluency: {avg_fluency:.1f}/30
  • Grammar & Vocabulary: {avg_grammar:.1f}/30

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 QUESTION BREAKDOWN:
"""
        
        for i, eval_data in enumerate(self.question_evaluations, 1):
            q_num = 7 + i
            q_total = eval_data.get("total_score", 0)
            q_completeness = eval_data.get("completeness", {}).get("score", 0)
            q_fluency = eval_data.get("fluency", {}).get("score", 0)
            q_grammar = eval_data.get("grammar", {}).get("score", 0)
            
            summary += f"""
Question {q_num}: {q_total:.1f}/100
  Completeness: {q_completeness}/40 | Fluency: {q_fluency}/30 | Grammar: {q_grammar}/30
"""
        
        summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next: Click "Next" to load another document or "Reset" to try again"""
        
        self.results_text.insert(tk.END, summary)
        self.results_text.config(state=tk.DISABLED)
        
        self.mic_button.config(state=tk.DISABLED, bg="#CCCCCC")
        self.next_button.config(text="➡️ Next Document", state=tk.NORMAL, bg="#2196F3")
        self.update_status(f"Part 4 Complete! Average score: {avg_total:.1f}/100", "green")
    
    def _reset(self) -> None:
        """Reset and load a new document"""
        self._load_document()
