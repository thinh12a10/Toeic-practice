"""
TOEIC Speaking Test - GUI Application for Part 2
Part 2: Describe a Picture Task - Speaking to describe an image
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import pyaudio
import time

from src.agents.speaking_agent import TOEICSpeakingAgent, UserProfile, Response
from src.core.part2_questions import Part2QuestionsEngine
from src.agents.evaluator_agent import ResponseEvaluator
from src.core.feedback import FeedbackGenerator


class Part2GUIApp:
    """GUI Application for TOEIC Speaking Test - Part 2 (Describe a Picture)"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application for Part 2
        
        Args:
            root: Tkinter root window
        """
        # ================= WINDOW SIZE FIX =================
        self.root = root
        self.root.title("TOEIC Speaking Test - Part 2: Describe a Picture")
        

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width * 0.9)
        height = int(screen_height * 0.8)

        # Center the window
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
        self.question_engine = Part2QuestionsEngine(level=self.user_profile.level)
        self.evaluator = ResponseEvaluator()
        self.feedback_generator = FeedbackGenerator()
        
        # State variables
        self.current_question: Optional[Dict[str, Any]] = None
        self.user_response_text: str = ""
        self.is_recording = False
        self.audio_frames = []
        self.audio_bytes: bytes = b''
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_loading_question = False  # Prevent concurrent question loads
        
        # Timer state
        self.preparation_time_remaining = 0
        self.speaking_time_remaining = 0
        self.in_preparation_phase = True  # Track if user is in prep or speaking phase
        
        # Session tracking
        self.session = None
        self.question_count = 0
        
        # Create UI first (before any status updates)
        self._create_ui()
        
        self.update_status("Initializing...", "blue")
        
        self._start_new_session()
        self._load_question()
    
    def _create_ui(self) -> None:
        """Create the user interface"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 2: Describe a Picture",
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
        
        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready. Read the prompt and prepare your description.",
            font=("Arial", 10),
            foreground="green"
        )
        self.status_label.pack(anchor=tk.W)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # =============== LEFT SIDE - INSTRUCTIONS ===============
        left_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(2, weight=1)
        
        instructions_label = ttk.Label(
            left_frame,
            text="Instructions:",
            font=("Arial", 11, "bold")
        )
        instructions_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Instructions text
        instructions_text = """
1. Read the picture description prompt carefully

2. You will have 10 seconds to prepare

3. After preparation time, click "START RECORDING"

4. You will have 45 seconds to describe the picture

5. Use complete sentences and descriptive language

6. Try to use varied vocabulary and grammar

7. Click "STOP RECORDING" when done or when time runs out

8. Click "NEXT QUESTION" to continue
        """
        
        instr_display = tk.Text(
            left_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=15
        )
        instr_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        instr_display.insert(tk.END, instructions_text)
        instr_display.config(state=tk.DISABLED)
        
        # =============== RIGHT SIDE - FEEDBACK ===============
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
        
        # Preparation timer label
        self.prep_timer_label = ttk.Label(
            controls_frame,
            text="Preparation time: --",
            font=("Arial", 10),
            foreground="blue"
        )
        self.prep_timer_label.pack(side=tk.LEFT, padx=20)
        
        # Separator
        sep1 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep1.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
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
        
        # Stop button (hidden)
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
        
        # Timer label for speaking
        self.speak_timer_label = ttk.Label(
            controls_frame,
            text="Speaking time: --",
            font=("Arial", 10),
            foreground="red"
        )
        self.speak_timer_label.pack(side=tk.LEFT, padx=20)
        
        # Separator
        sep2 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep2.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Next button
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
    
    def update_status(self, message: str, color: str = "black") -> None:
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
    
    def _start_new_session(self) -> None:
        """Start a new practice session"""
        self.session = self.agent.start_session()
        self.question_count = 0
        self.update_status("Session started. Ready for question 1.", "green")
    
    def _load_question(self) -> None:
        """Load a new Part 2 question asynchronously"""
        # Prevent concurrent loads
        if self.is_loading_question:
            return
        
        self.is_loading_question = True
        self.question_count += 1
        
        # Clean up previous state
        self.is_recording = False
        self.in_preparation_phase = True
        self.audio_frames = []  # Clear old audio frames
        self.user_response_text = ""
        
        # Disable controls
        self.mic_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        
        self.update_status(f"Loading question {self.question_count}...", "blue")
        
        # Load in background thread
        loading_thread = threading.Thread(target=self._load_question_background)
        loading_thread.daemon = True
        loading_thread.start()
    
    def _load_question_background(self) -> None:
        """Load question in background"""
        try:
            # Generate question
            self.current_question = self.question_engine.generate_question()
            
            # Update UI from main thread
            self.root.after(0, self._update_question_display)
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.update_status(f"❌ Error: {msg}", "red"))
            self.root.after(0, self._enable_controls)
            self.is_loading_question = False
    
    def _update_question_display(self) -> None:
        """Update question display"""
        # Ensure stop button is hidden and start recording button is shown
        self.stop_button.pack_forget()
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Update results text with picture description prompt
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        result_text = f"""Question {self.question_count}
Topic: {self.current_question.get('topic', 'General').upper()}
Difficulty: {self.current_question.get('difficulty', 'Unknown').upper()}

Picture Description Prompt:
{self.current_question.get('prompt', '')}

Status: Prepare your description (10 seconds)
        """
        
        self.results_text.insert(tk.END, result_text)
        self.results_text.config(state=tk.DISABLED)
        
        self.update_status("Question loaded. Preparation phase starting in 3 seconds...", "blue")
        self._enable_controls()
        
        # Start preparation phase after a brief delay
        self.root.after(3000, self._start_preparation_phase)
        
        # Mark question loading as complete
        self.is_loading_question = False
    
    def _enable_controls(self) -> None:
        """Enable controls"""
        self.mic_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
    
    def _start_preparation_phase(self) -> None:
        """Start the 10-second preparation phase"""
        self.in_preparation_phase = True
        self.preparation_time_remaining = 10
        self.mic_button.config(state=tk.DISABLED)  # Can't record during prep
        self.update_status("📖 PREPARATION PHASE: Read the prompt carefully (10 seconds)", "blue")
        self._run_preparation_timer()
    
    def _run_preparation_timer(self) -> None:
        """Run the preparation countdown timer"""
        if self.preparation_time_remaining > 0:
            self.prep_timer_label.config(text=f"Preparation time: {self.preparation_time_remaining}s")
            self.preparation_time_remaining -= 1
            self.root.after(1000, self._run_preparation_timer)
        else:
            # Preparation phase complete, ready to record
            self.in_preparation_phase = False
            self.prep_timer_label.config(text="Preparation time: DONE")
            self.update_status("🎤 SPEAKING PHASE: Start recording your description (45 seconds)", "blue")
            self.mic_button.config(state=tk.NORMAL)  # Now can record
    
    def _start_recording(self) -> None:
        """Start recording the picture description"""
        self.is_recording = True
        self.update_status("🔴 Recording... Describe the picture (45 seconds max).", "red")
        
        # Update button state
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
            MAX_RECORD_TIME = 45  # 45 seconds for picture description
            
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
            
            # Record for max 45 seconds or until stopped
            while self.is_recording:
                elapsed = time.time() - start_time
                if elapsed >= MAX_RECORD_TIME:
                    self.is_recording = False
                    break
                
                remaining = int(MAX_RECORD_TIME - elapsed)
                self.root.after(0, lambda r=remaining: self.speak_timer_label.config(text=f"Speaking time: {r}s"))
                
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except Exception as e:
                    print(f"⚠ Recording error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if self.audio_frames:
                self._process_recorded_audio()
        
        except Exception as e:
            self.update_status(f"❌ Recording error: {str(e)}", "red")
        finally:
            self.is_recording = False
            self.root.after(0, self._stop_recording)
    
    def _stop_recording(self) -> None:
        """Stop recording"""
        self.is_recording = False
        self.speak_timer_label.config(text="Speaking time: --")
        
        # Update button state
        self.stop_button.pack_forget()
        self.mic_button.pack(side=tk.LEFT, padx=5)
        self.update_status("Recording stopped. Processing...", "blue")
    
    def _process_recorded_audio(self) -> None:
        """Process recorded audio in background"""
        self.update_status("🔄 Processing your response... (recognizing speech & evaluating)", "blue")
        
        # Process in background thread
        processing_thread = threading.Thread(target=self._process_audio_background)
        processing_thread.daemon = True
        processing_thread.start()
    
    def _process_audio_background(self) -> None:
        """Background thread for audio processing and evaluation"""
        try:
            # Convert audio frames to audio data
            audio_bytes = b''.join(self.audio_frames)
            self.audio_bytes = audio_bytes
            
            # Recognize speech
            self.root.after(0, lambda: self.update_status("🎤 Recognizing speech...", "blue"))
            try:
                # Create AudioData object with proper parameters
                # sr.AudioData(audio_bytes, sample_rate, sample_width)
                audio_data = sr.AudioData(audio_bytes, 16000, 2)
                result = self.recognizer.recognize_google(audio_data)
                self.user_response_text = result
            except sr.UnknownValueError:
                self.user_response_text = "[Speech not recognized]"
            except sr.RequestError as e:
                self.user_response_text = f"[API error: {e}]"
            except Exception as e:
                self.user_response_text = f"[Recognition error: {str(e)}]"
            
            # Get evaluation feedback
            self.root.after(0, lambda: self.update_status("📊 Evaluating your response...", "blue"))
            self.root.after(0, self._get_feedback)
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.update_status(f"❌ Error processing audio: {msg}", "red"))
    
    def _get_feedback(self) -> None:
        """Get evaluation feedback in background"""
        feedback_thread = threading.Thread(target=self._get_feedback_background)
        feedback_thread.daemon = True
        feedback_thread.start()
    
    def _get_feedback_background(self) -> None:
        """Background thread for getting feedback"""
        try:
            # Get evaluation (this can be slow with LLM)
            result = self.evaluator.evaluate(
                user_response=self.user_response_text,
                audio_bytes=self.audio_bytes,
                question=self.current_question,
                user_level=self.user_profile.level
            )
            
            # Extract total score (already 0-10 scale)
            total_score = result.get('total_score', 0)
            
            # Get feedback text from evaluator result
            evaluation = {
                'score': int(total_score * 10),  # Convert 0-10 to 0-100
                'feedback': self._format_evaluation_feedback(result)
            }
            
            # Update UI from main thread
            self.root.after(0, lambda: self._display_feedback(evaluation))
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.update_status(f"❌ Error getting feedback: {msg}", "red"))
    
    def _display_feedback(self, evaluation: Dict[str, Any]) -> None:
        """Display feedback on UI"""
        try:
            # Update results display
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete("1.0", tk.END)
            
            feedback_text = f"""Question {self.question_count}
Topic: {self.current_question.get('topic', 'General').upper()}

Picture Description Prompt:
{self.current_question.get('prompt', '')}

Your Response:
"{self.user_response_text}"

Score: {evaluation.get('score', 0)}/100
Feedback:
{evaluation.get('feedback', 'No feedback available')}
            """
            
            self.results_text.insert(tk.END, feedback_text)
            self.results_text.config(state=tk.DISABLED)
            
            self.update_status("✓ Evaluation complete. Click NEXT QUESTION to continue.", "green")
            self.mic_button.config(state=tk.DISABLED)
        
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"❌ Error displaying feedback: {error_msg}", "red")
    
    def _format_evaluation_feedback(self, result_dict: Optional[Dict[str, Any]]) -> str:
        """Format evaluation scores into readable feedback"""
        if not result_dict:
            return "Unable to generate detailed feedback."
        
        feedback_lines = []
        
        # Extract scores from the evaluation result
        if 'pronunciation' in result_dict and isinstance(result_dict['pronunciation'], dict):
            pron_score = result_dict['pronunciation'].get('score', 0)
            feedback_lines.append(f"• Pronunciation: {pron_score}/10 - {'Excellent' if pron_score >= 8 else 'Good' if pron_score >= 6 else 'Needs improvement'}")
            
            # Add pronunciation issues if available
            issues = result_dict['pronunciation'].get('issues', [])
            if issues:
                feedback_lines.append(f"  Issues: {', '.join(issues[:2])}")
        
        if 'intonation' in result_dict and isinstance(result_dict['intonation'], dict):
            inton_score = result_dict['intonation'].get('score', 0)
            feedback_lines.append(f"• Intonation: {inton_score}/10 - {'Excellent' if inton_score >= 8 else 'Good' if inton_score >= 6 else 'Needs improvement'}")
            
            # Add intonation issues if available
            issues = result_dict['intonation'].get('issues', [])
            if issues:
                feedback_lines.append(f"  Issues: {', '.join(issues[:2])}")
        
        if 'pausing' in result_dict and isinstance(result_dict['pausing'], dict):
            pausing_score = result_dict['pausing'].get('score', 0)
            feedback_lines.append(f"• Pausing/Phrasing: {pausing_score}/10 - {'Excellent' if pausing_score >= 8 else 'Good' if pausing_score >= 6 else 'Needs improvement'}")
            
            # Add pausing issues if available
            issues = result_dict['pausing'].get('issues', [])
            if issues:
                feedback_lines.append(f"  Issues: {', '.join(issues[:2])}")
        
        # Add general feedback if available
        if 'feedback' in result_dict:
            feedback_lines.append(f"\nOverall Feedback:\n{result_dict['feedback']}")
        
        return "\n".join(feedback_lines) if feedback_lines else "No detailed feedback available."
    
    def _next_question(self) -> None:
        """Load next question"""
        self._load_question()
    
    def _reset(self) -> None:
        """Reset current question"""
        self._load_question()
