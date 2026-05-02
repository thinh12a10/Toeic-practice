# Dictionary Feature - Quick Start Guide

## 🚀 Installation (3 steps)

### Step 1: Install pyttsx3
```bash
pip install pyttsx3
```
Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Set up an LLM Provider (Optional but Recommended)

#### Best Option: Ollama (Free, Local, Fastest)
1. Download from https://ollama.ai
2. Run: `ollama pull mistral`
3. Run: `ollama serve` (keep running in background)

#### Alternative: OpenAI API
1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

### Step 3: Run the Application
```bash
python gui_app.py
```

---

## 📖 How to Use

1. **Launch the app** → A question appears
2. **Look for blue underlined words** → These are clickable
3. **Hover over a word** → Light blue highlight appears
4. **Click on a word** → Definition popup appears

## 📚 What You'll See in the Popup

```
┌─────────────────────────────────────┐
│ ANNOUNCEMENT                        │
├─────────────────────────────────────┤
│ IPA: /əˈnaʊnsmənt/                 │
│ Pronunciation: sounds like          │
│               "uh-NOUNCE-ment"      │
│                                     │
│ [🔊 Speak Button]                  │
├─────────────────────────────────────┤
│ Definition:                         │
│ A public or official statement      │
│ (noun)                              │
├─────────────────────────────────────┤
│ Vietnamese Meaning (Nghĩa Tiếng Việt):
│ • thông báo                         │
│ • công bố                           │
├─────────────────────────────────────┤
│ Example:                            │
│ The announcement was made today.    │
├─────────────────────────────────────┤
│ [Close Button]                      │
└─────────────────────────────────────┘
```

## ✨ Features

| Feature | Details |
|---------|---------|
| 💬 English Definition | Clear, concise descriptions |
| 🎯 IPA Pronunciation | International Phonetic Alphabet |
| 🇻🇳 Vietnamese Meaning | Translation for Vietnamese speakers |
| 🔊 Audio Pronunciation | Click "Speak" to hear the word |
| 📖 Example Sentences | Context for better understanding |
| 💾 Smart Caching | First lookup: 1-3s, Next: instant |
| 🚀 No UI Freeze | Background processing |

---

## ⚙️ Configuration

### Environment Variables

**For OpenAI:**
```bash
export OPENAI_API_KEY=sk-your-api-key
```

**For Anthropic:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-api-key
```

**For Ollama:**
```bash
# No configuration needed, runs locally
```

---

## 🔧 Troubleshooting

### Words don't show as clickable
- ✓ Reload the question
- ✓ Words must be > 2 characters
- ✓ Common words are filtered

### "Cannot initialize TTS" warning
- ✓ Dictionary still works
- ✓ Only the Speak button won't work
- ✓ On Linux: `apt-get install espeak`

### Popup doesn't appear
- ✓ Check if LLM provider is running
- ✓ Wait 1-3 seconds for first lookup
- ✓ Check API key is set (for OpenAI/Anthropic)

### Slow performance
- ✓ First lookup: Normal (1-3 seconds)
- ✓ Next lookups: Instant (cached)
- ✓ Try Ollama for faster responses

---

## 📁 Files Created/Modified

**New Files:**
- ✨ `dictionary_agent.py` - Core LLM integration
- ✨ `dictionary_popup.py` - UI component
- ✨ `DICTIONARY_SKILL.md` - Technical documentation
- ✨ `DICTIONARY_IMPLEMENTATION.md` - Full user guide
- ✨ `word_cache.json` - Auto-generated cache

**Modified Files:**
- ✏️ `gui_app.py` - Added dictionary integration
- ✏️ `requirements.txt` - Added pyttsx3

---

## 🎓 Example Workflow

```
Step 1: App starts
Step 2: Question loads: "The procedure should be documented carefully"
Step 3: Blue underlined words appear: procedure, documented, carefully
Step 4: Hover over "procedure" → Light blue highlight
Step 5: Click "procedure" → Popup appears
Step 6: See:
   - IPA: /prəˈsɛdʒər/
   - Vietnamese: "quy trình, thủ tục"
   - Definition: "An established way of doing something"
Step 7: Click 🔊 Speak → Hear pronunciation
Step 8: Close popup, continue
Step 9: Next time you see "procedure" → Instant popup (cached!)
```

---

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Set up LLM provider (Ollama recommended)
3. ✅ Run the application
4. ✅ Try clicking on words in the question
5. ✅ Click the 🔊 Speak button to hear pronunciation
6. ✅ Enjoy learning with interactive vocabulary!

---

**Questions?** Check `DICTIONARY_IMPLEMENTATION.md` for detailed documentation.

**Ready to start?** 
```bash
python gui_app.py
```

Happy learning! 📚✨
