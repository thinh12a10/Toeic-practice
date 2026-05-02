# Dictionary Feature SKILL - Interactive Word Lookup for Part 1

## Overview
This SKILL implements an interactive dictionary feature for TOEIC Speaking Part 1. When users click on words in the question text, a popup displays comprehensive word information including IPA pronunciation, Vietnamese meaning, and audio pronunciation capability.

## Components

### 1. Dictionary Agent (`dictionary_agent.py`)
**Purpose:** AI-powered word lookup and information retrieval

**Key Features:**
- Fetches word data using LLM (Ollama, OpenAI, or Anthropic)
- Caches results for performance (word_cache.json)
- Extracts English words from text (filters stop words)
- Returns structured word information

**Main Methods:**
- `get_word_info(word)` - Gets IPA, Vietnamese meaning, definition, etc.
- `extract_words_from_text(text)` - Extracts clickable words from question
- `_initialize_llm()` - Auto-detects available LLM provider

**Output Structure:**
```python
{
    'word': str,
    'ipa': str,  # /word pronunciation/
    'pronunciation': str,  # Human description
    'vietnamese_meaning': str,  # Vietnamese translation
    'definition': str,  # English definition
    'part_of_speech': str,  # noun/verb/adjective/etc
    'example': str,  # Example sentence
    'phonetic_symbols': str  # Alternative phonetics
}
```

### 2. Dictionary Popup UI (`dictionary_popup.py`)
**Purpose:** Display word information in an elegant popup window

**Key Features:**
- Clean, organized popup window
- Three main sections:
  1. **Word & Pronunciation**
     - Word title (uppercase)
     - IPA symbols (red, large, bold)
     - Pronunciation description
     - 🔊 Speak button
  
  2. **Definition**
     - English definition
     - Part of speech label
  
  3. **Vietnamese Meaning**
     - Vietnamese translation (highlighted, orange box)
     - Example sentence

**TTS Integration:**
- Uses pyttsx3 for text-to-speech
- Runs in background thread to prevent UI freezing
- Click "🔊 Speak" button to hear pronunciation

### 3. GUI Integration (`gui_app.py`)
**Integration Points:**

1. **Import Dictionary Components:**
   ```python
   from dictionary_agent import DictionaryAgent
   from dictionary_popup import DictionaryPopup
   ```

2. **Initialize in `__init__`:**
   ```python
   self.dictionary_agent = DictionaryAgent()
   self.clickable_words: Dict[str, Dict[str, Any]] = {}
   ```

3. **Configure Text Tags:**
   ```python
   self.question_text.tag_config("clickable_word", underline=True, foreground="blue")
   self.question_text.tag_config("hover_word", background="#e3f2fd")
   ```

4. **Bind Mouse Events:**
   ```python
   self.question_text.bind("<Button-1>", self._on_text_click)
   self.question_text.bind("<Motion>", self._on_text_motion)
   ```

5. **Apply Word Tags When Loading Question:**
   In `_update_question_display()`:
   ```python
   self._apply_word_tags()
   ```

## Implementation Steps

### Step 1: Add Dictionary Agent
Create `dictionary_agent.py` with:
- LLM integration (auto-detect provider)
- Word caching mechanism
- Prompt engineering for accurate word info
- Stop word filtering

### Step 2: Add Dictionary Popup
Create `dictionary_popup.py` with:
- Popup window UI
- Three-component layout
- TTS button for audio pronunciation
- Centered positioning

### Step 3: Integrate with GUI
Update `gui_app.py`:
- Import dictionary modules
- Initialize dictionary agent in `__init__`
- Apply clickable tags to words
- Implement click/hover handlers
- Show popup on word click

## User Interaction Flow

1. **Question Loads** → Dictionary agent pre-processes text and extracts words
2. **Underlined Blue Words** → User sees clickable words in the question
3. **User Hovers** → Word highlights with light blue background
4. **User Clicks** → Popup appears with word info
5. **User Clicks "🔊 Speak"** → Word pronunciation plays via TTS
6. **Popup Shows:**
   - IPA: /wɜːd/
   - Pronunciation: "sounds like 'werd'"
   - Vietnamese: "từ, chữ"
   - Definition: "A unit of language"
   - Example: "This is a common word."

## LLM Provider Priority

1. **Ollama** (local, free, fastest)
2. **OpenAI** (if OPENAI_API_KEY set)
3. **Anthropic** (if ANTHROPIC_API_KEY set)
4. **Fallback** (default response with limited info)

## Dependencies

Add to `requirements.txt`:
```
pyttsx3>=2.90          # Text-to-speech engine
```

## Performance Considerations

- **Caching:** Word definitions cached in `word_cache.json` to avoid re-fetching
- **Threading:** LLM queries run in background to prevent UI freeze
- **Lazy Loading:** Words only looked up when clicked
- **Stop Words:** Filters common words (articles, prepositions) to reduce clutter

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-...          # For OpenAI provider
ANTHROPIC_API_KEY=sk-ant-...   # For Anthropic provider
```

### Cache Management
- Auto-saves to `word_cache.json`
- Call `dictionary_agent.clear_cache()` to reset

## Testing

Example word lookups to test:
- "pronunciation" - Complex word, shows IPA clearly
- "Vietnamese" - Proper noun with Vietnamese meaning
- "document" - Common business word
- "frequently" - Adverb with proper description

## Future Enhancements

- Word audio examples from external APIs (Forvo)
- Part-of-speech color coding in question text
- Spaced repetition tracking for learned words
- Custom word lists/flashcards
- Offline dictionary database (SQLite)
