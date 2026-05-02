# TOEIC Speaking Test - Part 1 Quick Start Guide

## ⚡ 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py

# 3. Click "🎤 Start Recording" and read the text aloud!
```

## 🎯 What You'll Experience

### GUI Interface
- Clean, simple window with reading passages
- Green microphone button to start recording
- Real-time feedback and scoring
- Clear English text to read

### Workflow
1. **Read** - Text appears on screen for you to read
2. **Record** - Click microphone button and speak
3. **Evaluate** - AI evaluates your pronunciation and fluency
4. **Get Feedback** - See your score (0-10) and improvement tips
5. **Next** - Click next button for another question

### Scoring Components
- 📊 **Score**: 0-10 points
- 🗣️ **Fluency**: How smooth your speech is
- 🎯 **Pronunciation**: How clearly you speak
- ✍️ **Grammar**: Correct usage of English
- 📚 **Vocabulary**: Word variety and appropriateness
- 🧠 **Coherence**: Clarity and organization

## 🖼️ GUI Features

### Main Screen
```
┌─────────────────────────────────────────────┐
│  TOEIC Speaking Test - Part 1: Read Aloud   │
│  Level: BEGINNER | User: Test User          │
├─────────────────────────────────────────────┤
│  Read the following text aloud:             │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ "Hello, my name is John. I work in  │   │
│  │  a big company downtown."           │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ⏱️ Speaking time: 45 seconds               │
│                                             │
│  [🎤 Start Recording]                      │
│  Ready to record. Click the button.        │
└─────────────────────────────────────────────┘
```

## 📋 Sample Session Flow

```
START APP
   ↓
SESSION 1: New UI window opens
   ↓
QUESTION 1: "Hello, my name is John."
   ├─ You read: "Hello, my name is John."
   ├─ App scores: 8.5/10
   ├─ Feedback: "Good pronunciation! Try speaking more slowly."
   └─ [Next Question] ← Click here
   ↓
QUESTIONS 2-6: Repeat process
   ↓
APP CLOSES: Window closes when you exit
```

## 🎤 Recording Tips

✅ **Do:**
- Speak clearly and naturally
- Maintain even pace
- Pronounce each word distinctly
- Use proper intonation
- Take a breath before starting

❌ **Don't:**
- Speak too fast
- Mumble or slur words
- Have loud background noise
- Pause for too long
- Read too slowly

## 📊 Understanding Your Score

| Score | Level | Meaning |
|-------|-------|---------|
| 9-10  | 🌟 Excellent | Native-like fluency |
| 7-8   | 👍 Very Good | Good command of English |
| 5-6   | 💪 Good | Acceptable for exam |
| 3-4   | ⚠️ Fair | Needs improvement |
| 0-2   | 📝 Needs Work | Start over |

## 🔧 Difficulty Levels

Edit line in `gui_app.py` to change:

```python
# Line ~53 - Change "beginner" to:
level="beginner"        # Simple everyday sentences
level="intermediate"    # Standard TOEIC level
level="advanced"        # Complex business topics
```

## ⚠️ Common Issues & Solutions

### Microphone Not Working
```bash
# Windows - Install PyAudio properly:
pip install pipwin
pipwin install pyaudio

# Then restart: python main.py
```

### "Could not understand audio"
- Reduce background noise
- Speak more clearly
- Check microphone is set as default input device
- Ensure internet connection (for speech recognition)

### GUI Window Doesn't Open
```bash
# Test tkinter:
python -m tkinter

# If error, tkinter needs to be installed
# (Usually comes with Python, but may need reinstall)
```

### Connection Error
- Check internet connection
- Ensure Google Speech Recognition API is accessible
- Try again (API may be temporarily down)

## 📚 Practice Tips for TOEIC Success

1. **Practice every day** - 10-15 minutes daily is better than one long session
2. **Record yourself** - Listen back to identify problem areas
3. **Vary topics** - Use intermediate/advanced levels for variety
4. **Focus on weak areas** - Re-read problematic sentences
5. **Mirror native speakers** - Watch English speakers and copy their intonation
6. **Slow down** - Speak at a comfortable, clear pace
7. **Open your mouth** - Clear pronunciation is key

## 🚀 Next Steps After Learning Part 1

After you're comfortable with Part 1, future versions will have:
- ✅ Part 1: Read Aloud (YOU ARE HERE)
- ⏳ Part 2: Repeat Sentence
- ⏳ Part 3: Describe Picture
- ⏳ Part 4: Respond to Question
- ⏳ Part 5: Read and Respond
- ⏳ Part 6: Opinion Question

## 📞 Need Help?

1. **Installation issues**: See `SETUP.md`
2. **Technical problems**: Check console error messages
3. **Usage questions**: See `README.md`
4. **Microphone setup**: Check Windows/Mac/Linux audio settings

## 🎯 Your First Session Walkthrough

### Step 1: Open Terminal/Command Prompt
```bash
cd d:\Projects\AI agents\toeic_speaking_agent
```

### Step 2: Start App
```bash
python main.py
```

### Step 3: See GUI Window
```
✓ GUI Application loaded successfully!
✓ Microphone is ready for input

💡 Instructions:
  1. Read the text aloud when prompted
  2. Click the microphone button to start recording
  3. The app will evaluate your response
  4. Click 'Next Question' to continue
```

### Step 4: Recording
1. Look at displayed text silently (understand it first)
2. Click green 🎤 button
3. Read the text clearly and naturally
4. Stop clicking or wait for auto-stop
5. See your score and feedback

### Step 5: Next Question
1. Read feedback carefully
2. Click "➡️ Next Question"
3. Repeat steps 4-5

### Step 6: Finish
Close the window when done!

## 💡 Example Feedback

```
📊 YOUR RESPONSE SCORE: 7.5/10

📝 Your Response:
"Hello, my name is John. I work downtown."

💬 Feedback:
✅ Excellent! Your response was very strong.

📌 Task Analysis:
- You covered the main text well.
- Your reading was clear and at good pace.

💪 Strengths:
- Good pronunciation of all words
- Natural rhythm and intonation

🎯 Areas for Improvement:
- Speak slightly more slowly for better clarity
- Ensure clear pause between sentences
- Project voice a bit more

📈 Next Steps:
- Practice with more complex sentences
- Focus on sentence pauses
- Record yourself to hear improvements
```

## 🎉 Ready?

```bash
python main.py
```

**Let's practice! Good luck! 🌟**

---

For more detailed info, see:
- `README.md` - Complete documentation
- `SETUP.md` - Installation troubleshooting
- Console output - Real-time error messages