# TOEIC Speaking Practice AI Agent

A Python-based AI agent that provides TOEIC Speaking practice with intelligent question generation, response evaluation, and personalized feedback. Start with **Part 1: Read Aloud** with microphone support and real-time audio transcription.

## 🎯 Features

### Part 1: Read Aloud (✅ Implemented)
- **6 sentences/passages** to read aloud
- **GUI-based interface** with tkinter
- **Microphone recording** with real-time transcription
- **Automatic evaluation** based on TOEIC criteria
- **Personalized feedback** with improvement suggestions
- **Score range**: 0-10

### Future Parts
- Part 2: Repeat a sentence
- Part 3: Say a sentence based on picture
- Part 4: Respond to a question
- Part 5: Read information and respond
- Part 6: Express an opinion

## 📋 Evaluation Criteria

Each response is scored based on:
- **Fluency (20%)**: Smoothness, pacing, hesitations
- **Grammar (25%)**: Grammatical accuracy in response
- **Vocabulary (20%)**: Word choice and range
- **Coherence (15%)**: Organization and clarity
- **Pronunciation (20%)**: Clarity and accent

## 📁 Project Structure

```
toeic_speaking_agent/
├── main.py                  # GUI launcher entry point
├── gui_app.py              # GUI application (Part 1)
├── part1_questions.py      # Part 1 question engine
├── agent.py                # Core agent logic
├── questions.py            # General question engine
├── evaluator.py            # Response evaluation
├── feedback.py             # Feedback generation
├── requirements.txt        # Dependencies
├── SETUP.md               # Installation guide
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# For Windows users with PyAudio issues, see SETUP.md
```

### 2. Run the Application

```bash
python main.py
```

### 3. Use the GUI

1. Read the displayed text aloud
2. Click "🎤 Start Recording" button
3. Read the text clearly and naturally
4. Recording stops automatically (max 60 seconds)
5. Review your score and feedback
6. Click "➡️ Next Question" to continue

## 🤖 LLM Question Generation (NEW!)

The agent now supports **dynamic question generation** using local or cloud LLMs:

### Free Option: Ollama (Recommended) 🎉

Run TOEIC questions locally with **zero cost**:

```bash
# 1. Download Ollama from https://ollama.ai
# 2. Start Ollama server
ollama serve

# 3. In another terminal, download a model (3-8 GB)
ollama run mistral

# 4. Run the agent
python main.py
```

**Benefits**:
- ✅ 100% Free
- ✅ Unlimited questions
- ✅ Private (no data sent anywhere)
- ✅ Instant local inference

**See**: [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed setup

### Cloud Option: OpenAI/Anthropic (Optional)

Use cloud APIs if you prefer:
```env
OPENAI_API_KEY=sk-...        # ~$0.002 per question
ANTHROPIC_API_KEY=sk-ant-... # ~$0.001 per question
```

**See**: [DYNAMIC_GENERATION.md](DYNAMIC_GENERATION.md) for setup

### Fallback: Hardcoded Questions

If no LLM is available, the system automatically falls back to ~30 hardcoded questions per level.

---

## 💻 System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows 10/11, macOS, Linux
- **Microphone**: USB or built-in audio input
- **Internet**: Required for Google Speech Recognition API
- **RAM**: 512MB minimum, 1GB recommended

## 📦 Dependencies

### Core Requirements
- `SpeechRecognition>=3.10.0` - Audio transcription
- `pyaudio>=0.2.13` - Microphone support

### Optional Dependencies
- `anthropic>=0.3.0` - For Claude API integration
- `openai>=0.27.0` - For OpenAI API integration
- `pytest>=7.0` - For testing

## 🎮 Usage Examples

### Basic Usage (GUI)
```bash
python main.py
```

### Programmatic Usage
```python
from gui_app import TOEICGUIApp
import tkinter as tk

root = tk.Tk()
app = TOEICGUIApp(root)
root.mainloop()
```

### Generate Part 1 Questions
```python
from part1_questions import Part1QuestionEngine

engine = Part1QuestionEngine(level="beginner")
question = engine.generate_question()
print(question['text'])  # Text to read aloud
```

### Evaluate Responses
```python
from evaluator import ResponseEvaluator
from feedback import FeedbackGenerator

evaluator = ResponseEvaluator()
feedback_gen = FeedbackGenerator()

# Evaluate a response
score = evaluator.evaluate(user_response, question, user_level)

# Generate feedback
feedback = feedback_gen.generate_feedback(user_response, question, score)
```

## 📊 Difficulty Levels

### Beginner
- Simple, everyday sentences
- Basic vocabulary and grammar
- Pronunciation emphasis
- Good for practice starting out

### Intermediate
- Business and professional contexts
- Moderate vocabulary
- Varied sentence structures
- Standard TOEIC difficulty

### Advanced
- Complex business topics
- Advanced vocabulary and phrases
- Sophisticated sentence structures
- Challenge level practice

## 🎤 Microphone Tips

For best results:
- Use an external USB microphone if possible
- Position microphone 6-12 inches from mouth
- Minimize background noise
- Speak clearly at normal pace
- Ensure good internet connection for transcription

## 🐛 Troubleshooting

### Common Issues

**"No module named 'pyaudio'"**
- See SETUP.md for platform-specific installation
- Try: `pip install pipwin && pipwin install pyaudio`

**"No microphone detected"**
- Check system audio settings
- Ensure microphone is default input device
- Restart application after connecting microphone

**"Could not understand audio"**
- Speak more clearly
- Reduce background noise
- Check internet connection
- Try speaking slower

**"Connection error"**
- Verify internet connection
- Google Speech Recognition API may be temporarily down
- Try again in a few moments

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## 📈 Session Tracking

The application tracks:
- Questions answered
- Scores for each response
- Average session score
- Response feedback history
- Session duration

## 🎯 Future Enhancements

- [ ] Additional TOEIC parts (2-6)
- [ ] Detailed pronunciation analysis
- [ ] Custom question creation
- [ ] Session replay and review
- [ ] Progress tracking across sessions
- [ ] Integration with OpenAI/Claude for enhanced evaluation
- [ ] Picture-based questions (Part 3)
- [ ] Multi-choice response options
- [ ] Export reports

## 📄 API Reference

### TOEICGUIApp

Main GUI application class for Part 1 testing.

```python
class TOEICGUIApp:
    def __init__(self, root: tk.Tk)
    def _start_new_session() -> None
    def _load_question() -> None
    def _start_recording() -> None
    def _stop_recording() -> None
    def _evaluate_response() -> None
    def _show_results(score: float, feedback: str) -> None
    def _next_question() -> None
```

### Part1QuestionEngine

Question generation for Part 1 (Read Aloud) with dynamic LLM support.

```python
class Part1QuestionEngine:
    def __init__(self, level: str = "beginner", use_llm: bool = True)
    def generate_question() -> Dict[str, Any]  # Auto-selects LLM or fallback
    def get_part1_sequence(num_questions: int = 6) -> List[Dict]
    def get_generation_source() -> str  # Returns "ollama", "openai", "anthropic", or "hardcoded"
    def enable_llm(enabled: bool = True) -> None  # Toggle LLM at runtime
```

**Priority Order**:
1. Ollama (local, free)
2. OpenAI API (if OPENAI_API_KEY set)
3. Anthropic API (if ANTHROPIC_API_KEY set)
4. Hardcoded questions (always available as fallback)

### ResponseEvaluator

Evaluation logic for scoring responses.

```python
class ResponseEvaluator:
    def evaluate(user_response: str, question: Dict, user_level: str) -> float
```

### FeedbackGenerator

Feedback generation for responses.

```python
class FeedbackGenerator:
    def generate_feedback(user_response: str, question: Dict, score: float) -> str
```

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Additional question types and content
- Language improvements
- UI enhancements
- Performance optimizations
- Documentation improvements

## 📝 License

This project is provided as-is for educational purposes.

## 📞 Support

For issues or questions:
1. Check [SETUP.md](SETUP.md) for installation help
2. Review troubleshooting section above
3. Check console output for error messages
4. Verify system requirements are met

## 🙏 Acknowledgments

- Inspired by official TOEIC Speaking Test format
- Uses Google Speech Recognition API
- Built with Python, tkinter, and SpeechRecognition library

---

**Happy practicing! 🎯 Good luck with your TOEIC Speaking exam!**

## 📚 Core Components

### Agent (agent.py)
- **TOEICSpeakingAgent**: Main agent class managing the practice session
- **SessionState**: Tracks current session data (questions, responses, scores)
- **UserProfile**: User information and preferences
- **Response**: Individual response with score and feedback

### Question Engine (questions.py)
- **QuestionEngine**: Generates TOEIC-style questions
- Supports 4 main task types:
  - Read aloud (short texts)
  - Repeat sentences
  - Respond to questions
  - Express opinions

### Evaluator (evaluator.py)
- **ResponseEvaluator**: Scores responses on multiple dimensions
- Criteria:
  - Fluency (20%) - length, coherence, sentence structure
  - Grammar (25%) - accuracy, variety
  - Vocabulary (20%) - appropriateness, diversity
  - Coherence (15%) - task completion, organization
  - Pronunciation (20%) - clarity (simulated for text)

### Feedback Generator (feedback.py)
- **FeedbackGenerator**: Creates personalized feedback
- Provides:
  - Score-based encouragement
  - Task-specific analysis
  - Common error identification
  - Specific improvement suggestions
  - Learning recommendations

## 💡 Usage Example

```python
from agent import TOEICSpeakingAgent, UserProfile

# Create user profile
user_profile = UserProfile(
    user_id="user_001",
    name="John Learner",
    level="intermediate"
)

# Initialize agent
agent = TOEICSpeakingAgent(user_profile)

# Start session
agent.start_session()

# Get a question
question = agent.get_next_question()
print(question['instruction'])
print(question.get('question_text', question.get('text')))

# Process user response
response = agent.process_response("Your spoken answer here")
print(f"Score: {response.score}/10")
print(f"Feedback:\n{response.feedback}")

# End session and get summary
summary = agent.end_session()
print(f"Average score: {summary['average_score']:.2f}/10")
```

## 📊 Scoring System

Responses are scored from 0-10 based on:

| Score Range | Level | Feedback |
|-------------|-------|----------|
| 9.0-10.0 | Excellent | Strong command of the task |
| 8.0-8.9 | Very Good | Solid response with minor areas |
| 7.0-7.9 | Good | Demonstrates understanding |
| 5.0-6.9 | Fair | Adequate but needs improvement |
| 3.0-4.9 | Needs Work | Significant improvements needed |
| 0-2.9 | Poor | Response incomplete or off-task |

## 🔧 Enhancement Ideas

1. **Audio Integration**
   - Add speech recognition for voice input
   - Implement pronunciation analysis
   - Support audio playback of model answers

2. **LLM Integration**
   - Use Claude/GPT for more sophisticated evaluation
   - Generate creative new questions
   - Provide more nuanced feedback

3. **Database Persistence**
   - Store user profiles and session history
   - Track progress over time
   - Analyze performance trends

4. **Advanced Features**
   - Adaptive difficulty (adjust questions based on performance)
   - Peer comparison and leaderboards
   - Timed practice sessions
   - Question randomization and custom topics

5. **UI/UX**
   - Web interface with React
   - Desktop app with Tkinter/PySimpleGUI
   - Mobile app support

## 📝 Notes

- The evaluator uses heuristic-based scoring (can be enhanced with ML)
- Pronunciation evaluation is simulated for text (enable with actual speech recognition)
- Question bank is currently limited (can be expanded significantly)
- Feedback is rule-based (can be enhanced with LLM)

## 📄 License

This is a practice project for TOEIC Speaking preparation.

## 🤝 Contributing

To extend this agent:
1. Add more questions to the database
2. Improve evaluation criteria
3. Enhance feedback generation
4. Add audio support
5. Integrate with LLM for better scoring

---

**Happy practicing!** 🎯
