# TOEIC Speaking Test - Setup Guide

## Prerequisites

- **Python 3.8+** installed and available in PATH
- **Microphone** connected to your computer
- **Internet connection** (required for Google Speech Recognition API)

## Installation Steps

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: System-Level Installation (Platform Specific)

#### **Windows 10/11**

For Windows, PyAudio can be tricky. Try these approaches in order:

**Option A: Using pipwin (Recommended)**
```bash
pip install pipwin
pipwin install pyaudio
```

**Option B: Using pre-built wheel**
1. Download PyAudio wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Download the file matching your Python version (e.g., `pyaudio‑0.2.13‑cp39‑cp39‑win_amd64.whl` for Python 3.9)
3. Install it:
   ```bash
   pip install path/to/downloaded_wheel.whl
   ```

**Option C: Using conda**
```bash
conda install -c anaconda pyaudio
```

#### **macOS**

```bash
brew install portaudio
pip install pyaudio
```

#### **Linux (Ubuntu/Debian)**

```bash
sudo apt-get install python3-pyaudio
# or
pip install pyaudio
```

### Step 3: Verify Installation

Test if the setup is working:

```bash
python -c "import pyaudio; import speech_recognition; print('✓ All dependencies installed successfully!')"
```

## Running the Application

### Launch the GUI Application

```bash
python main.py
```

The application will:
1. Open a GUI window with the TOEIC Speaking Test interface
2. Display a reading passage that you need to read aloud
3. Provide a microphone button to record your voice
4. Transcribe your speech and evaluate your response
5. Display your score and feedback

## Features

### Part 1: Read Aloud
- 6 sentences/passages to read
- 45 seconds per question
- Evaluation criteria:
  - Pronunciation
  - Fluency
  - Intonation
  - Accuracy

### Scoring
- Score range: 0-10
- Based on:
  - **Fluency (20%)**: Smoothness and pacing of speech
  - **Grammar (25%)**: Grammatical accuracy
  - **Vocabulary (20%)**: Word choice and range
  - **Coherence (15%)**: Organization and clarity
  - **Pronunciation (20%)**: Clarity and accent

### Feedback
- Specific strengths highlighted
- Areas for improvement identified
- Actionable suggestions provided

## Troubleshooting

### Issue: "No module named 'pyaudio'"

**Solution:**
- Ensure you've completed Step 2 (System-Level Installation)
- Try Option B (pre-built wheel) for Windows

### Issue: "No microphone detected"

**Solution:**
1. Check if microphone is connected and enabled in system settings
2. Open Control Panel → Sound Settings → Input devices
3. Ensure your microphone is set as default device
4. Some anti-virus software may block microphone access

### Issue: "Could not understand audio"

**Solution:**
1. Speak clearly and at normal volume
2. Ensure there's minimal background noise
3. Check internet connection (needed for Google Speech Recognition)
4. Try speaking slower for better recognition

### Issue: "Service error" or "Connection error"

**Solution:**
1. Check your internet connection
2. The application requires Google Speech Recognition API
3. Try again in a moment (API may be temporarily unavailable)

### Issue: GUI doesn't appear on Windows

**Solution:**
1. Ensure tkinter is installed: `python -m tkinter`
2. If tkinter is missing, reinstall Python and check "tcl/tk and IDLE" during installation

## Audio Recording Tips

For best results:
1. **Use a good quality microphone**: Built-in laptop microphones work but external USB microphones are better
2. **Minimize background noise**: Close windows, turn off fans, ask others to be quiet
3. **Speak clearly**: Pronounce words clearly and maintain proper pace
4. **Proper distance**: Keep microphone about 6-12 inches from your mouth
5. **Lighting quality audio**: Ensure your microphone is not muted or at very low volume

## First Time User Walkthrough

1. Run `python main.py`
2. GUI window opens with a reading passage
3. Read the text carefully first (silent reading)
4. Click the green "🎤 Start Recording" button
5. Read the text aloud clearly and naturally
6. Click "⏹️ Stop Recording" (or app auto-stops after ~60 seconds)
7. Wait for transcription and evaluation
8. Review your score and feedback
9. Click "➡️ Next Question" to continue to next question
10. Practice all 6 questions in Part 1
11. Close the window when done

## Difficulty Levels

You can modify the difficulty level by editing [gui_app.py](gui_app.py):

```python
self.user_profile = UserProfile(
    user_id=str(uuid.uuid4())[:8],
    name="Test User",
    level="beginner"  # Change to "intermediate" or "advanced"
)
```

Available levels:
- **beginner**: Simple sentences (good for starting out)
- **intermediate**: Moderate complexity (TOEIC standard)
- **advanced**: Complex sentences with advanced vocabulary

## System Requirements

- **RAM**: Minimum 512MB (1GB+ recommended)
- **Disk Space**: 100MB for dependencies
- **Internet**: Required for speech recognition
- **Microphone**: USB or built-in audio input device

## Need Help?

If you encounter issues:
1. Check this troubleshooting guide
2. Review console output for error messages
3. Try uninstalling and reinstalling: `pip uninstall SpeechRecognition pyaudio -y && pip install -r requirements.txt`
4. Try a different microphone if available
5. Restart your computer and try again

## Next Steps

After completing Part 1 (Read Aloud), future versions will include:
- **Part 2**: Repeat a sentence
- **Part 3**: Say a sentence based on picture
- **Part 4**: Respond to a question
- **Part 5**: Read information and respond
- **Part 6**: Express an opinion

Enjoy practicing! 🎯
