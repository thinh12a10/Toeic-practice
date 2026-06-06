"""
TOEIC Speaking Test - GUI Application for Part 3
Part 3: Questions & Response Task - Answering questions about a scenario
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
from src.core.part3_questions import Part3QuestionsEngine
from src.agents.gemini_part3_evaluator import GeminiPart3Evaluator
from src.core.feedback import FeedbackGenerator


class Part3GUIApp:
    """GUI Application for TOEIC Speaking Test - Part 3 (Questions & Response)"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application for Part 3
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("TOEIC Speaking Test - Part 3: Questions & Response")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width * 0.9)
        height = int(screen_height * 0.85)

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
        self.question_engine = Part3QuestionsEngine(level=self.user_profile.level)
        self.evaluator = GeminiPart3Evaluator()
        self.feedback_generator = FeedbackGenerator()
        
        # State variables
        self.current_question_set: Optional[Dict[str, Any]] = None
        self.current_question_index: int = 0
        self.user_responses: List[str] = []
        self.question_evaluations: List[Dict[str, Any]] = []  # Store evaluations for each question
        self.is_recording = False
        self.audio_frames = []
        self.audio_bytes: bytes = b''
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_loading_question = False
        
        # Timer state
        self.preparation_time_remaining = 0
        self.speaking_time_remaining = 0
        self.in_preparation_phase = True
        
        # Session tracking
        self.session = None
        self.scenario_count = 0
        self.current_scenario: str = ""  # Store current scenario for results display
        
        # Create UI
        self._create_ui()
        
        self.update_status("Initializing...", "blue")
        
        self._start_new_session()
        self._load_question_set()
    
    def _create_ui(self) -> None:
        """Create the user interface"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 3: Questions & Response",
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
            text="Ready. Read the scenario and prepare your answers.",
            font=("Arial", 10),
            foreground="green"
        )
        self.status_label.pack(anchor=tk.W)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # =============== LEFT SIDE - SCENARIO & QUESTIONS ===============
        left_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        
        # Scenario label
        scenario_label = ttk.Label(
            left_frame,
            text="Scenario:",
            font=("Arial", 11, "bold")
        )
        scenario_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Scenario display
        self.scenario_text = tk.Text(
            left_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=4
        )
        self.scenario_text.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.scenario_text.config(state=tk.DISABLED)
        
        # Questions label
        questions_label = ttk.Label(
            left_frame,
            text="Questions:",
            font=("Arial", 11, "bold")
        )
        questions_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Questions display
        self.questions_text = tk.Text(
            left_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=10
        )
        self.questions_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.questions_text.config(state=tk.DISABLED)
        
        # =============== RIGHT SIDE - INSTRUCTIONS & FEEDBACK ===============
        right_frame = ttk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.rowconfigure(1, weight=1)
        
        # Instructions label
        instr_label = ttk.Label(
            right_frame,
            text="Instructions & Results:",
            font=("Arial", 11, "bold")
        )
        instr_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Instructions and feedback display
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
        
        # Display initial instructions
        self._display_instructions()
        
        # Controls frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Question counter
        self.question_counter_label = ttk.Label(
            controls_frame,
            text="Question: 1/3",
            font=("Arial", 10),
            foreground="blue"
        )
        self.question_counter_label.pack(side=tk.LEFT, padx=20)
        
        # Separator
        sep1 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep1.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Preparation timer label
        self.prep_timer_label = ttk.Label(
            controls_frame,
            text="Preparation time: --",
            font=("Arial", 10),
            foreground="blue"
        )
        self.prep_timer_label.pack(side=tk.LEFT, padx=20)
        
        # Separator
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
        
        # Timer label for speaking
        self.speak_timer_label = ttk.Label(
            controls_frame,
            text="Speaking time: --",
            font=("Arial", 10),
            foreground="red"
        )
        self.speak_timer_label.pack(side=tk.LEFT, padx=20)
        
        # Separator
        sep3 = ttk.Separator(controls_frame, orient=tk.VERTICAL)
        sep3.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
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
    
    def _display_instructions(self) -> None:
        """Display instructions in the results text box"""
        instructions = """TOEIC SPEAKING PART 3 - INSTRUCTIONS

How this test works:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. You will see a scenario (workplace situation)

2. Then 3 specific questions about that scenario

3. For EACH question:
   • You have 10 seconds to PREPARE
   • Then 15 seconds to RESPOND
   • Click "START RECORDING" to begin

4. Speak clearly and naturally

5. Your response will be evaluated for:
   • Pronunciation
   • Grammar
   • Vocabulary usage
   • Fluency
   • Answer relevance

6. After all 3 questions, you can:
   • Review feedback
   • Go to next scenario
   • Or reset to try again

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:
• Listen carefully to each question
• Think about your answer during prep time
• Speak in complete sentences
• Don't rush - use all 15 seconds
• Focus on clarity over perfection

Ready? Load a question to begin! ✓"""
        
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
    
    def _load_question_set(self) -> None:
        """Load a new question set (scenario with 3 questions)"""
        if self.is_loading_question:
            return
        
        self.is_loading_question = True
        self.update_status("Loading question set...", "blue")
        
        def load_in_thread():
            try:
                question_set = self.question_engine.get_next_question()
                
                if not question_set:
                    self.root.after(0, lambda: self.update_status(
                        "Failed to load questions. Please try again.",
                        "red"
                    ))
                    return
                
                self.current_question_set = question_set
                self.current_question_index = 0
                self.user_responses = ["", "", ""]
                self.scenario_count += 1
                
                self.root.after(0, self._display_question_set)
                self.root.after(0, lambda: self.update_status(
                    "Ready to start. Read the scenario and questions.",
                    "green"
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(
                    f"Error loading questions: {str(e)}",
                    "red"
                ))
            finally:
                self.is_loading_question = False
        
        thread = threading.Thread(target=load_in_thread, daemon=True)
        thread.start()
    
    def _display_question_set(self) -> None:
        """Display the current question set"""
        if not self.current_question_set:
            return
        
        # Store current scenario for results display
        self.current_scenario = self.current_question_set.get("scenario", "")
        self.question_evaluations = []  # Reset evaluations for new scenario
        
        # Display scenario
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.delete(1.0, tk.END)
        self.scenario_text.insert(tk.END, self.current_scenario)
        self.scenario_text.config(state=tk.DISABLED)
        
        # Display all questions
        self.questions_text.config(state=tk.NORMAL)
        self.questions_text.delete(1.0, tk.END)
        
        questions = self.current_question_set.get("questions", [])
        for idx, question in enumerate(questions, 1):
            self.questions_text.insert(tk.END, f"Question {idx}:\n{question}\n\n")
        
        self.questions_text.config(state=tk.DISABLED)
        
        # Reset for first question
        self._prepare_next_question()
    
    def _prepare_next_question(self) -> None:
        """Prepare for the next question"""
        if self.current_question_index >= 3:
            self._show_scenario_complete()
            return
        
        # Update counter
        self.question_counter_label.config(
            text=f"Question: {self.current_question_index + 1}/3"
        )
        
        # Highlight current question
        self._highlight_current_question()
        
        # Start preparation timer
        self.in_preparation_phase = True
        self.preparation_time_remaining = 10
        
        self.update_status(
            f"Question {self.current_question_index + 1}: Preparation phase...",
            "blue"
        )
        self.mic_button.config(state=tk.DISABLED, bg="#CCCCCC")
        self.next_button.config(state=tk.DISABLED, bg="#CCCCCC")
        
        self._run_preparation_timer()
    
    def _highlight_current_question(self) -> None:
        """Highlight the current question in the questions display"""
        self.questions_text.config(state=tk.NORMAL)
        
        # Remove previous tags
        self.questions_text.tag_remove("current", 1.0, tk.END)
        
        # Find and highlight current question
        question_num = self.current_question_index + 1
        start = self.questions_text.search(f"Question {question_num}:", 1.0, tk.END)
        if start:
            # Find end of question
            next_q = self.questions_text.search(f"Question {question_num + 1}:", start, tk.END)
            if next_q:
                end = next_q
            else:
                end = tk.END
            
            self.questions_text.tag_add("current", start, end)
            self.questions_text.tag_config("current", background="#FFFF99", foreground="#000000")
        
        self.questions_text.config(state=tk.DISABLED)
    
    def _run_preparation_timer(self) -> None:
        """Run the preparation timer"""
        if self.preparation_time_remaining > 0:
            self.prep_timer_label.config(
                text=f"Preparation time: {self.preparation_time_remaining}s"
            )
            self.preparation_time_remaining -= 1
            self.root.after(1000, self._run_preparation_timer)
        else:
            # Preparation complete, ready to record
            self.prep_timer_label.config(text="Preparation time: 0s")
            self.in_preparation_phase = False
            self.mic_button.config(state=tk.NORMAL, bg="#4CAF50")
            self.update_status(
                f"Question {self.current_question_index + 1}: Ready to record. Click the microphone button.",
                "green"
            )
    
    def _start_recording(self) -> None:
        """Start recording user response"""
        self.is_recording = True
        self.update_status(f"🔴 Recording... Answer the question (15 seconds max).", "red")
        
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
            MAX_RECORD_TIME = 15  # 15 seconds for question response
            
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
            
            # Record for max 15 seconds or until stopped
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
            self.root.after(0, lambda: self.update_status(f"❌ Recording error: {str(e)}", "red"))
        finally:
            self.is_recording = False
            self.root.after(0, self._stop_recording)
    
    def _process_recorded_audio(self) -> None:
        """Process the recorded audio"""
        self.update_status("Processing response...", "blue")
        
        def process_in_thread():
            try:
                # Convert audio frames to bytes
                if not self.audio_frames:
                    error_msg = "No audio data recorded"
                    self.root.after(0, lambda: self.update_status(error_msg, "red"))
                    return
                
                # Create audio bytes from frames
                audio_data = io.BytesIO()
                with wave.open(audio_data, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes(b''.join(self.audio_frames))
                
                audio_bytes = audio_data.getvalue()
                
                # Get placeholder text for response
                response_text = f"[Audio response - Question {self.current_question_index + 1}]"
                
                # Store response
                self.user_responses[self.current_question_index] = response_text
                
                # Get current question
                current_question = self.current_question_set.get("questions", [])[self.current_question_index]
                scenario = self.current_question_set.get("scenario", "")
                
                # Evaluate response with Gemini Part 3 evaluator
                evaluation = self.evaluator.evaluate(
                    audio_bytes=audio_bytes,
                    user_response=response_text,
                    question={"text": current_question, "task_type": "respond"},
                    scenario=scenario,
                    user_level=self.user_profile.level
                )
                
                # Store evaluation result
                self.question_evaluations.append({
                    "question_index": self.current_question_index,
                    "question_text": current_question,
                    "evaluation": evaluation
                })
                
                # Extract score from evaluation
                score = evaluation.get("total_score", 5.0)
                
                # Generate feedback with correct parameters
                feedback = self.feedback_generator.generate_feedback(
                    user_response=response_text,
                    question={"text": current_question, "task_type": "respond"},
                    score=score
                )
                
                # Display feedback
                self.root.after(0, self._display_question_feedback, feedback, response_text, evaluation)
                
                # Enable next button
                self.root.after(0, lambda: self.next_button.config(state=tk.NORMAL, bg="#2196F3"))
                self.root.after(0, lambda: self.update_status(
                    "Response recorded. Click 'Next Question' to continue.",
                    "green"
                ))
            
            except Exception as e:
                error_msg = f"Error processing response: {str(e)}"
                self.root.after(0, lambda: self.update_status(
                    error_msg,
                    "red"
                ))
        
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()
    
    def _stop_recording(self) -> None:
        """Stop recording"""
        self.is_recording = False
        self.speak_timer_label.config(text="Speaking time: --")
        
        # Update button state
        self.stop_button.pack_forget()
        self.mic_button.pack(side=tk.LEFT, padx=5)
        self.update_status("Recording stopped. Processing...", "blue")
    
    def _display_question_feedback(self, feedback: str, response: str, evaluation: Dict[str, Any]) -> None:
        """Display feedback for the current question with evaluation scores"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Extract scores from evaluation
        vocab_score = evaluation.get("vocabulary", {}).get("score", 0)
        grammar_score = evaluation.get("grammar", {}).get("score", 0)
        fluency_score = evaluation.get("fluency", {}).get("score", 0)
        comprehension_score = evaluation.get("comprehension", {}).get("score", 0)
        content_score = evaluation.get("content", {}).get("score", 0)
        total_score = evaluation.get("total_score", 0)
        
        # Extract feedback details
        vocab_feedback = evaluation.get("vocabulary", {}).get("feedback", "")
        grammar_feedback = evaluation.get("grammar", {}).get("feedback", "")
        fluency_feedback = evaluation.get("fluency", {}).get("feedback", "")
        comprehension_feedback = evaluation.get("comprehension", {}).get("feedback", "")
        content_feedback = evaluation.get("content", {}).get("feedback", "")
        
        display_text = f"""Question {self.current_question_index + 1} - Evaluation Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCORES (out of max points):
  • Vocabulary: {vocab_score}/25
  • Grammar: {grammar_score}/25
  • Fluency: {fluency_score}/25
  • Comprehension: {comprehension_score}/15
  • Content Relevance: {content_score}/10
  
  TOTAL: {total_score}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 DETAILED FEEDBACK:

Vocabulary: {vocab_feedback}
Grammar: {grammar_feedback}
Fluency: {fluency_feedback}
Comprehension: {comprehension_feedback}
Content: {content_feedback}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click "Next Question" to move to Question {min(self.current_question_index + 2, 3)}"""
        
        self.results_text.insert(tk.END, display_text)
        self.results_text.config(state=tk.DISABLED)
    
    def _show_scenario_complete(self) -> None:
        """Show scenario completion with detailed evaluation results"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Calculate overall statistics
        total_scores = []
        vocab_scores = []
        grammar_scores = []
        fluency_scores = []
        comprehension_scores = []
        content_scores = []
        
        for eval_data in self.question_evaluations:
            eval_result = eval_data.get("evaluation", {})
            total_scores.append(eval_result.get("total_score", 0))
            vocab_scores.append(eval_result.get("vocabulary", {}).get("score", 0))
            grammar_scores.append(eval_result.get("grammar", {}).get("score", 0))
            fluency_scores.append(eval_result.get("fluency", {}).get("score", 0))
            comprehension_scores.append(eval_result.get("comprehension", {}).get("score", 0))
            content_scores.append(eval_result.get("content", {}).get("score", 0))
        
        # Calculate averages
        avg_total = sum(total_scores) / len(total_scores) if total_scores else 0
        avg_vocab = sum(vocab_scores) / len(vocab_scores) if vocab_scores else 0
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_comprehension = sum(comprehension_scores) / len(comprehension_scores) if comprehension_scores else 0
        avg_content = sum(content_scores) / len(content_scores) if content_scores else 0
        
        # Build results display
        summary = f"""🎉 SCENARIO COMPLETE! ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 OVERALL RESULTS (Average Scores):
  • TOTAL SCORE: {avg_total:.1f}/100
  • Vocabulary: {avg_vocab:.1f}/25
  • Grammar: {avg_grammar:.1f}/25
  • Fluency: {avg_fluency:.1f}/25
  • Comprehension: {avg_comprehension:.1f}/15
  • Content Relevance: {avg_content:.1f}/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 QUESTION BREAKDOWN:
"""
        
        for i, eval_data in enumerate(self.question_evaluations, 1):
            eval_result = eval_data.get("evaluation", {})
            q_total = eval_result.get("total_score", 0)
            q_vocab = eval_result.get("vocabulary", {}).get("score", 0)
            q_grammar = eval_result.get("grammar", {}).get("score", 0)
            q_fluency = eval_result.get("fluency", {}).get("score", 0)
            q_comprehension = eval_result.get("comprehension", {}).get("score", 0)
            q_content = eval_result.get("content", {}).get("score", 0)
            
            summary += f"""
Question {i}:
  Total: {q_total}/100 | Vocab: {q_vocab}/25 | Grammar: {q_grammar}/25
  Fluency: {q_fluency}/25 | Comprehension: {q_comprehension}/15 | Content: {q_content}/10
"""
        
        summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What next?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click "NEXT SCENARIO" to:
→ Load a new scenario with different questions
→ Continue practicing Part 3

Or click "RESET" to:
→ Practice this scenario again
→ Try different responses"""
        
        self.results_text.insert(tk.END, summary)
        self.results_text.config(state=tk.DISABLED)
        
        self.mic_button.config(state=tk.DISABLED, bg="#CCCCCC")
        self.next_button.config(state=tk.NORMAL, bg="#2196F3", text="➡️ Next Scenario")
        self.update_status(f"Scenario complete! Average score: {avg_total:.1f}/100", "green")
    
    def _next_question(self) -> None:
        """Move to next question"""
        self.current_question_index += 1
        
        if self.current_question_index >= 3:
            # Load new scenario
            self._load_question_set()
        else:
            # Next question in same scenario
            self._prepare_next_question()
    
    def _reset(self) -> None:
        """Reset current scenario"""
        self.current_question_index = 0
        self.user_responses = ["", "", ""]
        self.question_evaluations = []  # Reset evaluations
        self._prepare_next_question()
