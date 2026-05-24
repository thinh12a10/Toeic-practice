"""
TOEIC Speaking Test - GUI Application with Audio Recording
Part 1: Read Aloud Task
"""

import tkinter as tk
from tkinter import ttk
import threading
import speech_recognition as sr
from typing import Optional, Dict, Any
import uuid
import pyaudio
import io
import wave

from src.agents.speaking_agent import TOEICSpeakingAgent, UserProfile, Response
from src.core.part1_questions import Part1QuestionEngine
from src.agents.evaluator_agent import ResponseEvaluator
from src.agents.dictionary_agent import DictionaryAgent
from src.ui.dictionary_popup import DictionaryPopup


class TOEICGUIApp:
    """GUI Application for TOEIC Speaking Test - Part 1"""

    def __init__(self, root: tk.Tk):

        self.root = root
        self.root.title("TOEIC Speaking Test - Part 1: Read Aloud")

        # ================= WINDOW SIZE FIX =================
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width * 0.9)
        height = int(screen_height * 0.8)

        # Center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.configure(bg="#f0f0f0")

        # ================= COMPONENTS =================

        self.user_profile = UserProfile(
            user_id=str(uuid.uuid4())[:8],
            name="Test User",
            level="beginner"
        )

        self.agent = TOEICSpeakingAgent(self.user_profile)
        self.question_engine = Part1QuestionEngine(
            level=self.user_profile.level
        )

        self.evaluator = ResponseEvaluator()
        self.dictionary_agent = DictionaryAgent()

        # ================= STATE =================

        self.current_question: Optional[Dict[str, Any]] = None
        self.user_response_text = ""

        self.is_recording = False
        self.audio_frames = []

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.session = None
        self.question_count = 0

        # Dictionary support
        self.clickable_words = {}
        self.word_tags = {}

        # ================= UI =================

        self._create_ui()
        self._start_new_session()
        self._load_question()

    # =========================================================
    # UI
    # =========================================================

    def _create_ui(self):

        # =====================================================
        # ROOT LAYOUT
        # =====================================================

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # =====================================================
        # HEADER
        # =====================================================

        header_frame = ttk.Frame(self.root)
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(10, 5)
        )

        title_label = ttk.Label(
            header_frame,
            text="TOEIC Speaking Test - Part 1: Read Aloud",
            font=("Arial", 16, "bold")
        )

        title_label.pack()

        info_label = ttk.Label(
            header_frame,
            text=f"Level: {self.user_profile.level.upper()}",
            font=("Arial", 10),
            foreground="gray"
        )

        info_label.pack()

        # =====================================================
        # STATUS
        # =====================================================

        status_frame = ttk.Frame(self.root)

        status_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 5)
        )

        self.status_label = ttk.Label(
            status_frame,
            text="Ready to record.",
            font=("Arial", 10),
            foreground="green"
        )

        self.status_label.pack(anchor=tk.W)

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        content_frame = ttk.Frame(self.root)

        content_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10
        )

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # =====================================================
        # LEFT PANEL
        # =====================================================

        left_frame = ttk.Frame(
            content_frame,
            relief=tk.SUNKEN,
            borderwidth=2
        )

        left_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        question_label = ttk.Label(
            left_frame,
            text="Read the following text aloud:",
            font=("Arial", 11, "bold")
        )

        question_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 5)
        )

        instruction_label = ttk.Label(
            left_frame,
            text="⏱️ Speaking time: 45 seconds",
            font=("Arial", 9),
            foreground="blue"
        )

        instruction_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=(0, 5)
        )

        # ================= QUESTION TEXT =================

        question_container = ttk.Frame(left_frame)

        question_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        question_container.grid_rowconfigure(0, weight=1)
        question_container.grid_columnconfigure(0, weight=1)

        question_scrollbar = ttk.Scrollbar(question_container)

        question_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.question_text = tk.Text(
            question_container,
            font=("Segoe UI", 13),
            wrap=tk.WORD,
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=12,
            pady=12,
            yscrollcommand=question_scrollbar.set
        )

        self.question_text.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        question_scrollbar.config(
            command=self.question_text.yview
        )

        self.question_text.config(state=tk.DISABLED)

        # =====================================================
        # RIGHT PANEL
        # =====================================================

        right_frame = ttk.Frame(
            content_frame,
            relief=tk.SUNKEN,
            borderwidth=2
        )

        right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        right_frame.grid_rowconfigure(7, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        feedback_label = ttk.Label(
            right_frame,
            text="Feedback & Results:",
            font=("Arial", 11, "bold")
        )

        feedback_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 5)
        )

        # ================= PROGRESS BARS =================

        ttk.Label(
            right_frame,
            text="Pronunciation"
        ).grid(row=1, column=0, sticky="w", padx=10)

        self.pronunciation_bar = ttk.Progressbar(
            right_frame,
            maximum=10
        )

        self.pronunciation_bar.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 5)
        )

        ttk.Label(
            right_frame,
            text="Intonation & Stress"
        ).grid(row=3, column=0, sticky="w", padx=10)

        self.intonation_bar = ttk.Progressbar(
            right_frame,
            maximum=10
        )

        self.intonation_bar.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 5)
        )

        ttk.Label(
            right_frame,
            text="Pausing / Phrasing"
        ).grid(row=5, column=0, sticky="w", padx=10)

        self.pausing_bar = ttk.Progressbar(
            right_frame,
            maximum=10
        )

        self.pausing_bar.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 10)
        )

        # ================= RESULTS TEXT =================

        results_container = ttk.Frame(right_frame)

        results_container.grid(
            row=7,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        results_container.grid_rowconfigure(0, weight=1)
        results_container.grid_columnconfigure(0, weight=1)

        results_scrollbar = ttk.Scrollbar(results_container)

        results_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.results_text = tk.Text(
            results_container,
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            bg="#fffacd",
            fg="#333333",
            relief=tk.FLAT,
            padx=12,
            pady=12,
            yscrollcommand=results_scrollbar.set
        )

        self.results_text.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        results_scrollbar.config(
            command=self.results_text.yview
        )

        self.results_text.config(state=tk.DISABLED)

        # =====================================================
        # CONTROLS
        # =====================================================

        controls_frame = ttk.Frame(self.root)

        controls_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(2, weight=1)
        controls_frame.grid_columnconfigure(3, weight=1)

        self.mic_button = tk.Button(
            controls_frame,
            text="🎤 Start Recording",
            command=self._start_recording,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=12
        )

        self.mic_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5
        )

        self.stop_button = tk.Button(
            controls_frame,
            text="⏹️ Stop Recording",
            command=self._stop_recording,
            font=("Arial", 11, "bold"),
            bg="#f44336",
            fg="white",
            pady=12
        )

        # IMPORTANT:
        # Create hidden initially using lower()
        self.stop_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5
        )

        self.stop_button.grid_remove()

        self.next_button = tk.Button(
            controls_frame,
            text="➡️ Next Question",
            command=self._next_question,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            pady=12
        )

        self.next_button.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=5
        )

        self.reset_button = tk.Button(
            controls_frame,
            text="🔄 Reset",
            command=self._reset,
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            pady=12
        )

        self.reset_button.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=5
        )

    # =========================================================
    # SESSION
    # =========================================================

    def _start_new_session(self):
        self.session = self.agent.start_session()
        self.question_count = 0

    # =========================================================
    # QUESTIONS
    # =========================================================

    def _load_question(self):

        self.question_count += 1

        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)

        self.question_text.insert(
            tk.END,
            "⏳ Loading new question..."
        )

        self.question_text.config(state=tk.DISABLED)

        self.update_status("Loading question...", "blue")

        thread = threading.Thread(
            target=self._load_question_background,
            daemon=True
        )

        thread.start()

    def _load_question_background(self):

        try:
            self.current_question = self.question_engine.generate_question()

            self.root.after(0, self._update_question_display)

        except Exception as e:
            self.root.after(
                0,
                lambda err=e: self.update_status(f"❌ {err}", "red")
            )

    def _update_question_display(self):

        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)

        text = self.current_question.get("text", "")

        self.question_text.insert(tk.END, text)

        self._apply_word_tags()

        self.question_text.config(state=tk.DISABLED)

        self.update_status(
            "Question loaded. Click microphone to start.",
            "green"
        )

    # =========================================================
    # RECORDING
    # =========================================================

    def _start_recording(self):

        if self.is_recording:
            return

        self.is_recording = True

        self.update_status(
            "🔴 Recording...",
            "red"
        )

        # Hide start button
        self.mic_button.grid_remove()

        # Show stop button
        self.stop_button.grid()

        # Disable other buttons
        self.next_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self._record_audio,
            daemon=True
        )

        thread.start()

    def _record_audio(self):

        try:

            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()

            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            self.audio_frames = []

            while self.is_recording:
                data = stream.read(
                    CHUNK,
                    exception_on_overflow=False
                )

                self.audio_frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            if self.audio_frames:
                self._process_recorded_audio()

        except Exception as e:
            self.update_status(f"❌ Recording error: {e}", "red")

    def _stop_recording(self):

        if not self.is_recording:
            return

        self.is_recording = False

        # Hide stop button
        self.stop_button.grid_remove()

        # Restore start button
        self.mic_button.grid()

        # Re-enable controls
        self.next_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)

        self.update_status(
            "Processing speech...",
            "blue"
        )

    # =========================================================
    # AUDIO PROCESSING
    # =========================================================

    def _process_recorded_audio(self):

        try:

            audio_bytes = self._frames_to_wav_bytes(
                self.audio_frames
            )

            try:
                audio = sr.AudioData(
                    b''.join(self.audio_frames),
                    16000,
                    2
                )

                self.user_response_text = (
                    self.recognizer.recognize_google(audio)
                )

            except:
                self.user_response_text = "(Could not transcribe)"

            self.root.after(
                0,
                lambda: self._evaluate_response(audio_bytes)
            )

        except Exception as e:
            self.update_status(f"❌ {e}", "red")

    # =========================================================
    # EVALUATION
    # =========================================================

    def _evaluate_response(self, audio_bytes: bytes):

        try:

            evaluation = self.evaluator.evaluate(
                audio_bytes=audio_bytes,
                user_response=self.user_response_text,
                question=self.current_question,
                user_level=self.user_profile.level
            )

            total_score = evaluation.get("total_score", 0.0)

            response = Response(
                question_id=self.current_question.get("id", "unknown"),
                user_text=self.user_response_text,
                score=total_score,
                feedback=evaluation.get("overall_feedback", "")
            )

            self.session.add_response(response)

            self._show_results(evaluation)

        except Exception as e:
            self.update_status(f"❌ Evaluation error: {e}", "red")

    def _show_results(self, evaluation: Dict[str, Any]):

        total_score = evaluation.get("total_score", 0.0)

        pronunciation = evaluation.get("pronunciation", {})
        intonation = evaluation.get("intonation", {})
        pausing = evaluation.get("pausing", {})

        # ================= PROGRESS BARS =================

        self.pronunciation_bar["value"] = pronunciation.get("score", 0)
        self.intonation_bar["value"] = intonation.get("score", 0)
        self.pausing_bar["value"] = pausing.get("score", 0)

        # ================= FORMAT FUNCTION =================

        def format_section(title, data):

            score = data.get("score", 0)

            strengths = data.get("strengths", [])
            issues = data.get("issues", [])
            tips = data.get("improvement_tips", [])

            section = f"""
🎯 {title}: {score}/10

✅ Strengths:
"""

            if strengths:
                for item in strengths:
                    section += f"• {item}\n"
            else:
                section += "• None\n"

            section += "\n⚠️ Areas to Improve:\n"

            if issues:
                for item in issues:
                    section += f"• {item}\n"
            else:
                section += "• None\n"

            section += "\n💡 Tips:\n"

            if tips:
                for item in tips:
                    section += f"• {item}\n"
            else:
                section += "• None\n"

            return section

        # ================= RESULTS TEXT =================

        results_content = f"""
📊 TOTAL SCORE: {total_score:.1f}/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Your Response:
{self.user_response_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{format_section("Pronunciation", pronunciation)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{format_section("Intonation & Stress", intonation)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{format_section("Pausing / Phrasing", pausing)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Overall Feedback:
{evaluation.get("overall_feedback", "")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        self.results_text.config(state=tk.NORMAL)

        self.results_text.delete("1.0", tk.END)

        self.results_text.insert(tk.END, results_content)

        self.results_text.config(state=tk.DISABLED)

        self.results_text.yview_moveto(0)

        if not self.next_button.winfo_manager():
            self.next_button.pack(side=tk.LEFT, padx=5)

        self.update_status(
            "✅ Evaluation complete!",
            "green"
        )

    # =========================================================
    # NAVIGATION
    # =========================================================

    def _next_question(self):
        self._load_question()

    def _reset(self):

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

        self.pronunciation_bar["value"] = 0
        self.intonation_bar["value"] = 0
        self.pausing_bar["value"] = 0

        self._load_question()

    # =========================================================
    # STATUS
    # =========================================================

    def update_status(self, message, color="black"):

        self.status_label.config(
            text=message,
            foreground=color
        )

        self.root.update()

    # =========================================================
    # DICTIONARY
    # =========================================================

    def _apply_word_tags(self):

        if not self.current_question:
            return

        text_content = self.question_text.get(
            "1.0",
            tk.END
        ).strip()

        words = self.dictionary_agent.extract_words_from_text(
            text_content
        )

        self.question_text.config(state=tk.NORMAL)

        for word in words:

            start_pos = "1.0"

            while True:

                pos = self.question_text.search(
                    rf"\b{word}\b",
                    start_pos,
                    nocase=True,
                    regexp=True
                )

                if not pos:
                    break

                end_pos = f"{pos}+{len(word)}c"

                self.question_text.tag_add(
                    "clickable_word",
                    pos,
                    end_pos
                )

                start_pos = end_pos

        self.question_text.config(state=tk.DISABLED)

    def _on_text_click(self, event):

        pos = self.question_text.index(
            f"@{event.x},{event.y}"
        )

        word = self._get_word_at_position(pos)

        if not word:
            return

        self.update_status(
            f"📚 Fetching '{word}'...",
            "blue"
        )

        thread = threading.Thread(
            target=self._fetch_word_info_async,
            args=(word,),
            daemon=True
        )

        thread.start()

    def _on_text_motion(self, event):

        pos = self.question_text.index(
            f"@{event.x},{event.y}"
        )

        word = self._get_word_at_position(pos)

        self.question_text.tag_remove(
            "hover_word",
            "1.0",
            tk.END
        )

        if word:

            word_start = f"{pos} wordstart"
            word_end = f"{pos} wordend"

            self.question_text.tag_add(
                "hover_word",
                word_start,
                word_end
            )

            self.root.config(cursor="hand2")

        else:
            self.root.config(cursor="arrow")

    def _on_text_leave(self, event):

        self.question_text.tag_remove(
            "hover_word",
            "1.0",
            tk.END
        )

        self.root.config(cursor="arrow")

    def _get_word_at_position(self, pos):

        try:

            word_start = f"{pos} wordstart"
            word_end = f"{pos} wordend"

            word = self.question_text.get(
                word_start,
                word_end
            )

            word = word.strip(".,!?;:\"'()[]{}")

            return word if len(word) >= 3 else None

        except:
            return None

    def _fetch_word_info_async(self, word):

        try:

            word_info = self.dictionary_agent.get_word_info(word)

            self.root.after(
                0,
                lambda: self._show_dictionary_popup(word_info)
            )

        except Exception as e:
            print(e)

    def _show_dictionary_popup(self, word_info):

        popup = DictionaryPopup(
            self.root,
            word_info,
            on_close=lambda: self.update_status(
                "Ready",
                "green"
            )
        )

        popup.show()

    # =========================================================
    # WAV CONVERSION
    # =========================================================

    def _frames_to_wav_bytes(self, frames):

        buffer = io.BytesIO()

        wf = wave.open(buffer, 'wb')

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)

        wf.writeframes(b''.join(frames))

        wf.close()

        return buffer.getvalue()


# =============================================================
# MAIN
# =============================================================

def main():

    root = tk.Tk()

    app = TOEICGUIApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()