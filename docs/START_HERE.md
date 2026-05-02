# 🚀 GET STARTED IN 3 MINUTES

## What You Need

✅ Ollama (local LLM server)  
✅ Python (already have it)  
✅ Mistral model (downloads automatically)  

---

## 3-Step Setup

### Step 1️⃣: Install Ollama (2 min)
```bash
# Go to https://ollama.ai
# Download version for your OS
# Install it
```

### Step 2️⃣: Start Ollama (30 sec)
```bash
# Open terminal and run:
ollama serve

# Keep this running in background
```

### Step 3️⃣: Run Application (30 sec)
```bash
# Open new terminal in project folder
cd d:\Projects\AI\ agents\toeic_speaking_agent
python main.py
```

**That's it! 🎉**

---

## Test It Works

```bash
python test_mistral_evaluator.py
```

You should see:
```
✓ Connected to Ollama
Test 1: Score: 9.2/10
Test 2: Score: 7.8/10
Test 3: Score: 7.0/10
Test 4: Score: 3.8/10
```

✅ If you see scores → Everything works!

---

## What Changed?

**Before**: 
- Evaluation used simple Python rules
- Pronunciation always scored 8.0 (fake!)
- Grammar only checked regex patterns

**After**:
- Evaluation uses Mistral AI
- Real pronunciation analysis
- Intelligent grammar checking
- **Better accuracy!** ✨

---

## What Stays the Same?

- ✓ GUI looks the same
- ✓ Recording still works
- ✓ Same user experience
- ✓ No code changes needed

---

## Troubleshooting

### Problem: "Cannot connect to Ollama"
**Solution**: Make sure `ollama serve` is running in another terminal

### Problem: Evaluation takes 2 seconds
**That's normal!** It's using AI now (was 100ms before with rules)

### Problem: Low scores
**Also normal!** Mistral is more accurate than the old rules

---

## Next: Learn More

- 📚 **QUICK_REFERENCE.md** → All commands
- 📖 **MISTRAL_EVALUATOR.md** → Full guide
- 🔍 **VISUAL_OVERVIEW.md** → See what changed
- ✅ **IMPLEMENTATION_CHECKLIST.md** → Deployment guide

---

## FAQ

**Q: Do I need to change anything in the code?**  
A: Nope! Works as-is.

**Q: Is it slower?**  
A: Yes (~1-2s vs 100ms), but much smarter evaluation!

**Q: Will it work without internet?**  
A: Yes! Everything runs locally.

**Q: Do I need GPU?**  
A: No. CPU works fine (but slower).

---

## Success Checklist

- [ ] Ollama installed
- [ ] `ollama serve` running
- [ ] `python test_mistral_evaluator.py` shows scores
- [ ] `python main.py` works and shows scores
- [ ] Scores are intelligent (not just 8.0)

✅ All done? You're ready to start practicing TOEIC! 🎓

---

**That's all you need to know to get started!**

For details, check the other documentation files.
