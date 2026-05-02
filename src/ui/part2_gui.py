"""
TOEIC Speaking Test - GUI Application for Part 2
Part 2: Repeat Task - Listen and repeat spoken text
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
import time
import os
import tempfile

from src.agents.speaking_agent import TOEICSpeakingAgent, UserProfile, Response
from src.core.part2_questions import Part2QuestionsEngine
from src.core.text_to_speech import TextToSpeechGenerator
from src.agents.evaluator_agent import ResponseEvaluator
from src.core.feedback import FeedbackGenerator


class Part2GUIApp:
    """GUI Application for TOEIC Speaking Test - Part 2 (Repeat)"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application for Part 2
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("TOEIC Speaking Test - Part 2: Repeat")
        self.root.geometry("1200x850")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize components
        self.user_profile = UserProfile(
            user_id=str(uuid.uuid4())[:8],
            name="Test User",
            level="beginner"
        )
        self.agent = TOEICSpeakingAgent(self.user_profile)
        self.question_engine = Part2QuestionsEngine(level=self.user_profile.level)
        self.tts_generator = TextToSpeechGenerator(provider="pyttsx3")
        self.evaluator = ResponseEvaluator()
        self.feedback_generator = FeedbackGenerator()
        
        # State variables
        self.current_question: Optional[Dict[str, Any]] = None
        self.user_response_text: str = ""
        self.is_recording = False
        self.audio_frames = []
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_loading_question = False  # Prevent concurrent question loads
        
        # Audio playback state
        self.audio_data: Optional[bytes] = None
        self.is_playing = False
        self.audio_cache: Dict[str, bytes] = {}  # Cache generated audio
        self.next_audio_data: Optional[bytes] = None  # Pre-generated audio for next question
        
        # Timer state
        self.listening_time_remaining = 0
        self.recording_time_remaining = 0
        
        # Session tracking
        self.session = None
        self.question_count = 0
        
        # Create UI first (before any status updates)
        self._create_ui()
        
        # Pre-initialize TTS engine (avoid delay on first use)
        self.update_status("Initializing...", "blue")
        self._initialize_tts()
        
        self._start_new_session()
        self._load_question()
    
    def _create_ui(self) -> None:
        """Create the user interface"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 2: Repeat",
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
            text="Ready. Click PLAY AUDIO to hear the sentence.",
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
1. Click "PLAY AUDIO" button to hear the sentence

2. You will have 15 seconds to listen

3. After listening, click "START RECORDING"

4. You will have 15 seconds to repeat what you heard

5. Speak clearly and naturally

6. Click "STOP RECORDING" when done

7. Click "NEXT QUESTION" to continue
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
        
        # Play Audio button
        self.play_button = tk.Button(
            controls_frame,
            text="🔊 Play Audio",
            command=self._play_audio,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Timer label for listening
        self.listen_timer_label = ttk.Label(
            controls_frame,
            text="Listening time: --",
            font=("Arial", 10),
            foreground="blue"
        )
        self.listen_timer_label.pack(side=tk.LEFT, padx=20)
        
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
        
        # Timer label for recording
        self.record_timer_label = ttk.Label(
            controls_frame,
            text="Recording time: --",
            font=("Arial", 10),
            foreground="red"
        )
        self.record_timer_label.pack(side=tk.LEFT, padx=20)
        
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
    
    def _initialize_tts(self) -> None:
        """Pre-initialize TTS engine to avoid delay on first use"""
        try:
            # This initializes pyttsx3 immediately
            _ = self.tts_generator.engine
            print("✓ TTS engine pre-initialized")
        except Exception as e:
            print(f"⚠ TTS pre-initialization warning: {e}")
    
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
        self.audio_frames = []  # Clear old audio frames
        self.user_response_text = ""
        
        # Disable controls
        self.play_button.config(state=tk.DISABLED)
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
            sentence_text = self.current_question.get("text", "")
            
            # Check cache first, otherwise use pre-generated audio or generate new
            if sentence_text in self.audio_cache:
                self.audio_data = self.audio_cache[sentence_text]
            elif self.next_audio_data:
                self.audio_data = self.next_audio_data
                self.audio_cache[sentence_text] = self.audio_data
                self.next_audio_data = None
            else:
                self.audio_data = self.tts_generator.text_to_speech(sentence_text)
                self.audio_cache[sentence_text] = self.audio_data
            
            # Update UI from main thread
            self.root.after(0, self._update_question_display)
            
            # Pre-generate next question's audio in background
            self.root.after(0, self._pregenerate_next_audio)
        
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
        
        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        result_text = f"""Question {self.question_count}
Topic: {self.current_question.get('topic', 'General').upper()}
Difficulty: {self.current_question.get('difficulty', 'Unknown').upper()}

Sentence to repeat:
"{self.current_question.get('text', '')}"

Status: Ready to play audio
        """
        
        self.results_text.insert(tk.END, result_text)
        self.results_text.config(state=tk.DISABLED)
        
        self.update_status("Question loaded. Click PLAY AUDIO to hear the sentence.", "blue")
        self._enable_controls()
        
        # Mark question loading as complete
        self.is_loading_question = False
    
    def _enable_controls(self) -> None:
        """Enable controls"""
        self.play_button.config(state=tk.NORMAL)
        self.mic_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
    
    def _pregenerate_next_audio(self) -> None:
        """Pre-generate next question's audio in background while user works on current"""
        def generate_next():
            try:
                next_question = self.question_engine.generate_question()
                next_text = next_question.get("text", "")
                
                # Only generate if not already cached
                if next_text not in self.audio_cache:
                    self.next_audio_data = self.tts_generator.text_to_speech(next_text)
            except Exception as e:
                print(f"⚠ Next audio pre-generation failed: {e}")
        
        pregenerate_thread = threading.Thread(target=generate_next, daemon=True)
        pregenerate_thread.start()
    
    def _play_audio(self) -> None:
        """Play audio"""
        if self.is_playing:
            self.update_status("Audio is already playing...", "blue")
            return
        
        self.update_status("🔊 Playing audio... (15 seconds)", "blue")
        self.play_button.config(state=tk.DISABLED)
        self.mic_button.config(state=tk.DISABLED)
        
        play_thread = threading.Thread(target=self._play_audio_background)
        play_thread.daemon = True
        play_thread.start()
    
    def _play_audio_background(self) -> None:
        """Play audio in background"""
        try:
            import pyaudio
            import struct
            
            if not self.audio_data:
                self.root.after(0, lambda: self.update_status("❌ No audio data available", "red"))
                self.root.after(0, self._enable_controls)
                return
            
            self.is_playing = True
            
            # Save audio data to temporary file and play it
            fd, temp_audio = tempfile.mkstemp(suffix='.wav', text=False)
            os.close(fd)
            
            try:
                # Write audio to temporary file
                with open(temp_audio, 'wb') as f:
                    f.write(self.audio_data)
                
                # Play the audio file using pyaudio
                with wave.open(temp_audio, 'rb') as wav_file:
                    # Get audio parameters
                    n_channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    frame_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    
                    # Create pyaudio stream
                    p = pyaudio.PyAudio()
                    stream = p.open(
                        format=p.get_format_from_width(sample_width),
                        channels=n_channels,
                        rate=frame_rate,
                        output=True
                    )
                    
                    # Play audio in chunks
                    chunk_size = 1024
                    total_frames = n_frames
                    frames_played = 0
                    listening_time = 15  # Max 15 seconds
                    start_time = time.time()
                    
                    while frames_played < total_frames and self.is_playing:
                        elapsed = time.time() - start_time
                        if elapsed >= listening_time:
                            break
                        
                        data = wav_file.readframes(chunk_size)
                        if not data:
                            break
                        
                        stream.write(data)
                        frames_played += chunk_size
                        
                        # Update timer
                        remaining = listening_time - int(elapsed)
                        self.root.after(0, lambda r=remaining: self.listen_timer_label.config(text=f"Listening time: {r}s"))
                    
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
            
            finally:
                # Cleanup temp file
                if os.path.exists(temp_audio):
                    try:
                        os.remove(temp_audio)
                    except:
                        pass
            
            self.is_playing = False
            self.root.after(0, self._after_listening)
        
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Playback error: {str(e)}", "red"))
            self.is_playing = False
            self.root.after(0, self._enable_controls)
    
    def _after_listening(self) -> None:
        """After listening period ends"""
        self.listen_timer_label.config(text="Listening time: --")
        self.update_status("✓ Listening time complete. Click START RECORDING to begin your repetition.", "green")
        self.play_button.config(state=tk.NORMAL)
        self.mic_button.config(state=tk.NORMAL)
    
    def _start_recording(self) -> None:
        """Start recording"""
        self.is_recording = True
        self.update_status("🔴 Recording... Repeat what you heard (15 seconds max).", "red")
        
        # Update button state
        self.mic_button.pack_forget()
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.play_button.config(state=tk.DISABLED)
        
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
            MAX_RECORD_TIME = 15
            
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
                self.root.after(0, lambda r=remaining: self.record_timer_label.config(text=f"Recording time: {r}s"))
                
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
        self.record_timer_label.config(text="Recording time: --")
        
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
            audio_data = b''.join(self.audio_frames)
            
            # Recognize speech
            self.root.after(0, lambda: self.update_status("🎤 Recognizing speech...", "blue"))
            try:
                result = self.recognizer.recognize_google(
                    sr.AudioData(audio_data, 16000, 2)
                )
                self.user_response_text = result
            except sr.UnknownValueError:
                self.user_response_text = "[Speech not recognized]"
            except sr.RequestError as e:
                self.user_response_text = f"[API error: {e}]"
            
            # Get evaluation feedback
            self.root.after(0, lambda: self.update_status("📊 Evaluating your response...", "blue"))
            self.root.after(0, self._get_feedback)
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.update_status(f"❌ Error processing audio: {msg}", "red"))
    
    def _create_wav_from_frames(self, audio_data: bytes, rate: int, channels: int) -> bytes:
        """Create WAV file from audio frames"""
        import io
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(rate)
            wav_file.writeframes(audio_data)
        
        return wav_buffer.getvalue()
    
    def _get_feedback(self) -> None:
        """Get evaluation feedback in background"""
        feedback_thread = threading.Thread(target=self._get_feedback_background)
        feedback_thread.daemon = True
        feedback_thread.start()
    
    def _get_feedback_background(self) -> None:
        """Background thread for getting feedback"""
        try:
            # Get evaluation (this can be slow with LLM)
            score = self.evaluator.evaluate(
                user_response=self.user_response_text,
                question=self.current_question,
                user_level=self.user_profile.level
            )
            
            # Get feedback text from evaluator's last evaluation
            evaluation = {
                'score': int(score * 10),  # Convert 0-10 to 0-100
                'feedback': self._format_evaluation_feedback(self.evaluator.last_evaluation)
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

Original Sentence:
"{self.current_question.get('text', '')}"

Your Response:
"{self.user_response_text}"

Score: {evaluation.get('score', 0)}/100
Feedback:
{evaluation.get('feedback', 'No feedback available')}
            """
            
            self.results_text.insert(tk.END, feedback_text)
            self.results_text.config(state=tk.DISABLED)
            
            self.update_status("✓ Evaluation complete. Click NEXT QUESTION to continue.", "green")
            self.play_button.config(state=tk.DISABLED)
            self.mic_button.config(state=tk.DISABLED)
        
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"❌ Error displaying feedback: {error_msg}", "red")
    
    def _format_evaluation_feedback(self, scores_dict: Optional[Dict[str, float]]) -> str:
        """Format evaluation scores into readable feedback"""
        if not scores_dict:
            return "Unable to generate detailed feedback."
        
        feedback_lines = []
        
        if 'fluency' in scores_dict:
            fluency_score = scores_dict['fluency']
            feedback_lines.append(f"• Fluency: {fluency_score}/10 - {'Excellent' if fluency_score >= 8 else 'Good' if fluency_score >= 6 else 'Needs improvement'}")
        
        if 'pronunciation' in scores_dict:
            pron_score = scores_dict['pronunciation']
            feedback_lines.append(f"• Pronunciation: {pron_score}/10 - {'Excellent' if pron_score >= 8 else 'Good' if pron_score >= 6 else 'Needs improvement'}")
        
        if 'grammar' in scores_dict:
            grammar_score = scores_dict['grammar']
            feedback_lines.append(f"• Grammar: {grammar_score}/10 - {'Excellent' if grammar_score >= 8 else 'Good' if grammar_score >= 6 else 'Needs improvement'}")
        
        if 'vocabulary' in scores_dict:
            vocab_score = scores_dict['vocabulary']
            feedback_lines.append(f"• Vocabulary: {vocab_score}/10 - {'Excellent' if vocab_score >= 8 else 'Good' if vocab_score >= 6 else 'Needs improvement'}")
        
        if 'coherence' in scores_dict:
            coherence_score = scores_dict['coherence']
            feedback_lines.append(f"• Coherence: {coherence_score}/10 - {'Excellent' if coherence_score >= 8 else 'Good' if coherence_score >= 6 else 'Needs improvement'}")
        
        return "\n".join(feedback_lines) if feedback_lines else "No detailed feedback available."
    
    def _next_question(self) -> None:
        """Load next question"""
        self._load_question()
    
    def _reset(self) -> None:
        """Reset current question"""
        self._load_question()
