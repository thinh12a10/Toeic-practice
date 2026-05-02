#!/usr/bin/env python3
"""
Comparison Test: Old vs Improved Evaluator
Demonstrates improvements using your scoring rules
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.evaluator_agent import ResponseEvaluator
from src.agents.improved_evaluator_agent import ImprovedResponseEvaluator


def compare_evaluators():
    """Compare old vs new evaluator"""
    
    print("=" * 80)
    print("COMPARISON: Current vs IMPROVED Evaluator")
    print("=" * 80)
    print()
    
    # Initialize both
    print("🚀 Initializing evaluators...")
    old_evaluator = ResponseEvaluator()
    new_evaluator = ImprovedResponseEvaluator()
    print()
    
    if not old_evaluator.connected:
        print("⚠️  Ollama not running. Starting new evaluator demo anyway...\n")
    
    # Test cases - realistic responses
    test_cases = [
        {
            "name": "Perfect Match (No Errors)",
            "original": "My company is located in the downtown area of the city.",
            "response": "My company is located in the downtown area of the city.",
            "user_level": "beginner"
        },
        {
            "name": "Complete Text with Minor Errors",
            "original": "My company is located in the downtown area of the city.",
            "response": "My company is locate in the downtown area of the city.",
            "user_level": "beginner"
        },
        {
            "name": "Missing Some Words",
            "original": "My company is located in the downtown area of the city.",
            "response": "Company downtown area city.",
            "user_level": "beginner"
        },
        {
            "name": "Partial Coverage",
            "original": "My company is located in the downtown area of the city. We have about two hundred employees.",
            "response": "My company is downtown. Have many employees.",
            "user_level": "intermediate"
        },
        {
            "name": "Very Short (Incomplete)",
            "original": "My company is located in the downtown area of the city.",
            "response": "Downtown.",
            "user_level": "beginner"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"TEST {i}: {test['name']}")
        print("-" * 80)
        print(f"Original:  {test['original']}")
        print(f"Response:  {test['response']}")
        print(f"User Level: {test['user_level']}")
        print()
        
        question = {
            "id": f"test_{i}",
            "task_type": "read_aloud",
            "text": test['original'],
            "level": test['user_level']
        }
        
        # Evaluate with old system
        if old_evaluator.connected:
            print("OLD EVALUATOR (LLM-only):")
            old_score = old_evaluator.evaluate(test['response'], question, test['user_level'])
            print(f"  Score: {old_score:.1f}/10")
            if old_evaluator.last_evaluation:
                scores = old_evaluator.last_evaluation
                print(f"    Fluency: {scores['fluency']:.1f}, Pronunciation: {scores['pronunciation']:.1f}, Grammar: {scores['grammar']:.1f}")
        else:
            print("OLD EVALUATOR: Skipped (Ollama not connected)")
            old_score = None
        
        print()
        
        # Evaluate with new system
        print("IMPROVED EVALUATOR (Hybrid: LLM + Rules):")
        new_score = new_evaluator.evaluate(test['response'], question, test['user_level'])
        print(f"  Score: {new_score:.1f}/10")
        
        # Get detailed feedback
        details = new_evaluator.get_detailed_feedback(test['response'], question)
        print(f"  Text Coverage: {details['text_coverage']}")
        print(f"  Words Read: {details['words_read']}/{details['total_original_words']}")
        
        if details['missing_words']:
            print(f"  ❌ Missing: {', '.join(details['missing_words'][:5])}")
        
        if details['mispronounced_words']:
            print(f"  ⚠️  Mispronounced: {', '.join(details['mispronounced_words'][:5])}")
        
        print(f"  💡 Suggestions: {details['suggestions'][0]}")
        
        if old_score:
            diff = new_score - old_score
            print(f"\n  Score Difference: {diff:+.1f}")
        
        print("\n")
    
    print("=" * 80)
    print("KEY IMPROVEMENTS")
    print("=" * 80)
    print("""
✅ YOUR RULES NOW IMPLEMENTED:
   • Base score: 5.0 for reading full text
   • Bonus points (up to 5) for perfect reading
   • Deductions for each missing/mispronounced word
   • Word-level analysis with missing word detection

✅ BETTER PROMPTS FOR MISTRAL:
   • Task-specific evaluation (not generic)
   • Clear scoring calibration
   • Emphasizes reading accuracy
   
✅ DETAILED FEEDBACK:
   • Shows which words were missed
   • Shows which words were mispronounced
   • Text coverage percentage
   • Specific improvement suggestions

✅ HYBRID SCORING:
   • 60% rule-based (your scoring rules)
   • 40% LLM (quality assessment)
   • More consistent and predictable scores
   """)


if __name__ == "__main__":
    compare_evaluators()
