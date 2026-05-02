# Quick Reference - Using Ollama with TOEIC Agent

## 🚀 30-Second Setup

### Step 1: Install Ollama
Download from https://ollama.ai and complete installation

### Step 2: Start Ollama Server
```bash
ollama serve
```
Keep this running in the background.

### Step 3: Download Model (First Time Only)
```bash
# In a new terminal/command prompt
ollama run mistral
```

Wait for download to complete (~5-15 minutes depending on internet speed).

### Step 4: Run the Agent
```bash
# Make sure you're in the project directory
python main.py
```

## ✅ That's It!

The agent will automatically detect Ollama and use it for dynamic question generation.

---

## 🔍 Verify Setup

Check if Ollama is working:

```bash
# Should return JSON with available models
curl http://localhost:11434/api/tags
```

---

## 📖 Complete Setup with Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download Ollama from https://ollama.ai

# 3. Terminal 1 - Start Ollama server
ollama serve

# 4. Terminal 2 - Download model
ollama run mistral

# 5. Terminal 3 - Test the setup
python test_dynamic_questions.py

# You should see:
# ✓ Initialized Ollama (mistral) for dynamic question generation
```

---

## 🎮 Using the Agent

```python
from part1_questions import Part1QuestionEngine

# Auto-detects Ollama if running
engine = Part1QuestionEngine(level="intermediate")

# Generate questions
question = engine.generate_question()
print(question['text'])  # New question each time!
print(question['generated_by'])  # Should show "ollama"
```

---

## 🆘 Troubleshooting

### "Ollama connection failed"
```bash
# Make sure Ollama is running
ollama serve  # Run in a separate terminal
```

### "Model not found"
```bash
# Download the model
ollama run mistral
```

### Still getting hardcoded questions?
```bash
# Verify Ollama is listening
curl http://localhost:11434/api/tags

# If that fails, restart Ollama
# Kill the process and run: ollama serve
```

---

## 💡 Available Models

Best options for TOEIC:

| Model | Download Size | Speed |
|-------|---------------|-------|
| **mistral** | 3.8 GB | Fast ⚡ |
| orca-mini | 1.3 GB | Very Fast ⚪ |
| llama2 | 3.8 GB | Medium 🟡 |

### Try Different Model

```bash
# Stop current Ollama process
# Terminal 1
ollama run llama2

# Terminal 3
# Re-run your agent (will automatically use llama2)
python main.py
```

---

## 📊 Performance

With **Mistral model** on typical hardware:

| Aspect | Performance |
|--------|-------------|
| First question generation | 3-8 seconds (model loads) |
| Subsequent questions | 2-4 seconds |
| Question variety | Unlimited (generated) |
| Cost | FREE |
| Internet required | No (after setup) |

---

## 🎓 Common Questions

### Q: Can I use Ollama while offline?
**A**: Yes! After downloading the model, you can work completely offline.

### Q: Which model should I choose?
**A**: Start with **mistral** - it's fast, good quality, and reasonable size.

### Q: Can I change models later?
**A**: Yes, just download another model and update `.env`:
```env
OLLAMA_MODEL=llama2
```

### Q: What if I don't want to use Ollama?
**A**: The agent automatically falls back to hardcoded questions (~30 per level).

### Q: Can I use OpenAI instead?
**A**: Yes, add `OPENAI_API_KEY` to `.env` if no Ollama is running.

---

## 🔗 Related Documentation

- **[OLLAMA_SETUP.md](OLLAMA_SETUP.md)** - Detailed setup guide
- **[DYNAMIC_GENERATION.md](DYNAMIC_GENERATION.md)** - LLM generation details
- **[README.md](README.md)** - Main project readme
- **[.env.example](.env.example)** - Configuration template

---

## ✨ Next Steps

1. ✅ Install Ollama (https://ollama.ai)
2. ✅ Run `ollama serve`
3. ✅ Run `ollama run mistral`
4. ✅ Run `python main.py`
5. ✅ Enjoy unlimited TOEIC practice! 🎉

---

**Questions?** Check the troubleshooting section or refer to the full documentation files.
