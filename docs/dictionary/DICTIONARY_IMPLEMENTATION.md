# Dictionary Feature Implementation Guide

## Overview
The dictionary feature has been successfully integrated into the TOEIC Speaking Part 1 application. This feature allows users to click on words in the question text to view comprehensive word information including IPA pronunciation, Vietnamese meaning, and audio pronunciation.

## What Was Added

### 1. **New Files**

#### `dictionary_agent.py`
- **Purpose**: AI-powered word lookup agent
- **Features**:
  - Fetches word data using LLM (Ollama, OpenAI, or Anthropic)
  - Auto-detects available LLM provider
  - Caches word definitions locally in `word_cache.json`
  - Extracts English words from question text
  - Filters stop words (articles, prepositions, common words)

#### `dictionary_popup.py`
- **Purpose**: UI popup window for displaying word information
- **Components**:
  1. **Word & Pronunciation Section**
     - Word title (uppercase, blue)
     - IPA pronunciation (red, bold)
     - Pronunciation description
     - 🔊 Speak button for audio pronunciation
  
  2. **Definition Section**
     - English definition
     - Part of speech label
  
  3. **Vietnamese Meaning Section**
     - Vietnamese translation (orange highlight box)
     - Easy to read for Vietnamese speakers
  
  4. **Example Section**
     - Example sentence using the word
     - Context for better understanding

#### `DICTIONARY_SKILL.md`
- **Purpose**: Complete skill documentation
- **Content**: Architecture, usage guide, LLM setup, performance considerations

### 2. **Modified Files**

#### `gui_app.py`
**New Imports:**
```python
from dictionary_agent import DictionaryAgent
from dictionary_popup import DictionaryPopup
```

**New Variables in `__init__`:**
```python
self.dictionary_agent = DictionaryAgent()  # Initialize Dictionary Agent
self.clickable_words: Dict[str, Dict[str, Any]] = {}
self.word_tags: Dict[str, str] = {}
```

**New UI Configuration:**
- Text tag configuration for clickable words (blue, underlined)
- Text tag for hover highlighting (light blue background)
- Mouse event bindings:
  - `<Button-1>`: Word click → Show popup
  - `<Motion>`: Hover → Highlight word
  - `<Leave>`: Mouse leave → Remove highlight

**New Methods:**
- `_apply_word_tags()` - Apply clickable tags to words
- `_on_text_click(event)` - Handle word click
- `_on_text_motion(event)` - Handle mouse hover
- `_on_text_leave(event)` - Handle mouse leaving
- `_get_word_at_position(pos)` - Get word under cursor
- `_fetch_word_info_async(word)` - Fetch word info asynchronously
- `_show_dictionary_popup(word_info)` - Display popup

#### `requirements.txt`
Added dependency:
```
pyttsx3>=2.90          # Text-to-speech in dictionary feature
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure LLM Provider (Optional but Recommended)

#### Option A: Use Ollama (Local, Free, Fastest)
```bash
# Download and install Ollama from https://ollama.ai
# Then run:
ollama pull mistral
ollama serve
```

#### Option B: Use OpenAI API
```bash
# Set environment variable
export OPENAI_API_KEY=sk-your-api-key-here
```
Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

#### Option C: Use Anthropic Claude API
```bash
# Set environment variable
export ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 3. Run the Application
```bash
python gui_app.py
```

## Usage Guide

### How to Use the Dictionary Feature

1. **Start the Application**
   - Run `python gui_app.py`
   - Wait for a question to load

2. **Identify Clickable Words**
   - Words in blue and underlined are clickable
   - Common words (articles, prepositions) are filtered out
   - Minimum word length: 3 characters

3. **Click on a Word**
   - Move your mouse over a word → it highlights with light blue background
   - Click on the word → Popup appears with word information

4. **View Word Information**
   - **IPA**: International Phonetic Alphabet (how to read the pronunciation)
   - **Pronunciation**: Description of how to pronounce
   - **Vietnamese Meaning**: Translation in Vietnamese
   - **Definition**: English definition
   - **Part of Speech**: noun/verb/adjective/etc.
   - **Example**: Example sentence using the word

5. **Hear the Pronunciation**
   - Click the 🔊 **Speak** button to hear the word pronounced
   - The word will play through your speakers

6. **Close the Popup**
   - Click the **Close** button or close the popup window

### Example Workflow
```
Question loads: "The announcement was made during the conference."
↓
Underlined words appear: announcement, made, during, conference
↓
Click on "announcement"
↓
Popup shows:
  • IPA: /əˈnaʊnsmənt/
  • Pronunciation: "sounds like uh-NOUNCE-ment"
  • Vietnamese: "thông báo, công bố"
  • Definition: "A public or official statement"
  • Part of Speech: noun
  • Example: "The announcement will be made tomorrow."
↓
Click 🔊 Speak → Hear pronunciation
↓
Close popup and continue
```

## Performance & Caching

### Word Caching
- **Location**: `word_cache.json` (created automatically)
- **Benefit**: First lookup fetches from LLM, subsequent lookups are instant
- **Example**: Look up "announcement" once → cached for 2ms lookup next time

### Lazy Loading
- Words are only looked up when clicked
- No performance impact while reading questions
- Background thread fetches data without freezing UI

### Memory Usage
- Typical cache size: 1-5 MB for 100-500 words
- Clear cache anytime: `dictionary_agent.clear_cache()`

## LLM Provider Comparison

| Provider | Speed | Cost | Setup | Quality |
|----------|-------|------|-------|---------|
| **Ollama** | ⭐⭐⭐⭐⭐ | Free | Local download | Good |
| **OpenAI** | ⭐⭐⭐⭐ | API cost | API key only | Excellent |
| **Anthropic** | ⭐⭐⭐⭐ | API cost | API key only | Excellent |
| **Fallback** | ⭐⭐⭐ | Free | None | Limited |

## Troubleshooting

### Issue: Words don't appear as clickable
**Solution**: 
- Check that words are > 2 characters long
- Words might be filtered if they're in the stop words list
- Reload the question

### Issue: "Cannot initialize TTS" warning
**Solution**: This is non-fatal. The dictionary will still work; just the Speak button won't work.
- On Windows: Should work automatically
- On Mac: Might need to install additional audio drivers
- On Linux: Install: `apt-get install espeak` or `dnf install espeak`

### Issue: Popup doesn't appear after clicking
**Solution**:
- Check terminal for error messages
- Make sure an LLM provider is configured or running
- Wait a moment - first lookup might take a few seconds
- Check internet connection if using OpenAI/Anthropic

### Issue: Word definitions are inaccurate or incomplete
**Solution**:
- Make sure you're using Ollama/OpenAI/Anthropic (not fallback mode)
- Check LLM provider is running/API key is valid
- Try clearing cache: Delete `word_cache.json` and try again

### Issue: Application runs slowly with dictionary feature
**Solution**:
- First lookup: Normal (1-3 seconds for LLM)
- Subsequent lookups: Should be instant (cached)
- If slow: Use Ollama instead of API-based providers

## File Structure
```
toeic_speaking_agent/
├── gui_app.py                    # Updated with dictionary integration
├── dictionary_agent.py           # NEW - LLM-powered word lookup
├── dictionary_popup.py           # NEW - Popup UI for word info
├── part1_questions.py
├── agent.py
├── evaluator.py
├── feedback.py
├── requirements.txt              # Updated with pyttsx3
├── DICTIONARY_SKILL.md          # NEW - Skill documentation
├── DICTIONARY_IMPLEMENTATION.md # NEW - This file
├── word_cache.json              # AUTO-GENERATED - Word cache
└── ... (other files)
```

## API Reference

### DictionaryAgent Class

```python
from dictionary_agent import DictionaryAgent

agent = DictionaryAgent()

# Get comprehensive word information
word_info = agent.get_word_info("amazing")
# Returns: {
#     'word': 'amazing',
#     'ipa': '/əˈmeɪzɪŋ/',
#     'pronunciation': 'sounds like uh-MAY-zing',
#     'vietnamese_meaning': 'tuyệt vời, dị thường',
#     'definition': 'Extremely surprising or impressive',
#     'part_of_speech': 'adjective',
#     'example': 'The concert was amazing!',
#     'phonetic_symbols': 'ə-'meɪ-zɪŋ'
# }

# Extract words suitable for dictionary
words = agent.extract_words_from_text("The announcement was made.")
# Returns: ['announcement', 'made']

# Clear cache
agent.clear_cache()
```

### DictionaryPopup Class

```python
from dictionary_popup import DictionaryPopup

# Create popup
popup = DictionaryPopup(
    parent=root_window,
    word_info=word_info_dict,
    on_close=lambda: print("Popup closed")
)

# Show popup
popup.show()
```

## Advanced Configuration

### Customize Stop Words
Edit `dictionary_agent.py`, `extract_words_from_text()` method:
```python
stop_words = {
    # ... existing words ...
    'custom', 'word', 'to', 'exclude'
}
```

### Adjust Speech Rate
Edit `dictionary_popup.py`, `_initialize_tts()` method:
```python
self.tts_engine.setProperty('rate', 150)  # 150 = normal, 100 = slow, 200 = fast
```

### Change Ollama Model
Edit `dictionary_agent.py`, `_query_ollama()` method:
```python
"model": "neural-chat"  # or any other installed model
```

## Future Enhancements

Potential features to add:
- ✨ Word example sentences from real TOEIC tests
- ✨ Synonyms and antonyms
- ✨ Audio examples from native speakers (Forvo integration)
- ✨ Spaced repetition for learned words
- ✨ Flashcard mode for vocabulary review
- ✨ Custom word lists by difficulty level
- ✨ Offline dictionary database (SQLite)
- ✨ Multi-language support

## Support & Feedback

For issues or suggestions:
1. Check troubleshooting section above
2. Review DICTIONARY_SKILL.md for detailed architecture
3. Check terminal output for error messages
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Happy learning! Enjoy exploring vocabulary with the interactive dictionary! 📚✨**
