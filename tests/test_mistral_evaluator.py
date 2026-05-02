#!/usr/bin/env python3
"""
Test script for Mistral-based evaluator
Demonstrates how the LLM evaluation works
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.evaluator_agent import ResponseEvaluator
from src.core.part1_questions import Part1QuestionEngine

def test_mistral_evaluation():
    """Test the Mistral-based evaluation"""
    
    print("=" * 70)
    print("TOEIC Speaking Test - Mistral Evaluator Test")
    print("=" * 70)
    print()
    
    # Initialize evaluator
    print("🚀 Initializing Mistral Evaluator...")
    evaluator = ResponseEvaluator()
    
    if not evaluator.connected:
        print("\n⚠️  ERROR: Ollama is not running!")
        print("\nTo use the Mistral evaluator, please:")
        print("1. Install Ollama from https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Download Mistral model: ollama run mistral")
        print("4. Run this test again")
        return
    
    print("✓ Connected to Ollama\n")
    
    # Create a sample question
    question = {
        "id": "part1_001",
        "task_type": "read_aloud",
        "text": "My company is located in the downtown area of the city. We have about two hundred employees working in our office.",
        "topic": "work",
        "difficulty": "medium",
        "level": "beginner"
    }
    
    # Test responses
    test_responses = [
        {
            "text": "My company is located in the downtown area of the city. We have about two hundred employees working in our office.",
            "level": "intermediate",
            "expected": "Excellent - perfectly matches the original text"
        },
        {
            "text": "My company is downtown with two hundred peoples working there.",
            "level": "intermediate",
            "expected": "Good - captures main idea but slight grammar error (peoples -> employees)"
        },
        {
            "text": "Company is in downtown. Many employees work there.",
            "level": "beginner",
            "expected": "Fair - shorter, simpler, but complete"
        },
        {
            "text": "Big company. Downtown. Employees.",
            "level": "beginner",
            "expected": "Poor - too fragmented, minimal content"
        }
    ]
    
    print("📊 Testing Mistral-based evaluation...\n")
    
    for i, test in enumerate(test_responses, 1):
        print(f"Test {i}:")
        print(f"  Response: {test['text'][:60]}...")
        print(f"  User Level: {test['level']}")
        print(f"  Expected: {test['expected']}")
        
        # Evaluate
        print("  🔄 Evaluating with Mistral...", end=" ", flush=True)
        score = evaluator.evaluate(test['text'], question, test['level'])
        print()
        
        # Show scores
        if evaluator.last_evaluation:
            scores = evaluator.last_evaluation
            print(f"  Score: {score:.1f}/10")
            print(f"    - Fluency: {scores['fluency']:.1f}")
            print(f"    - Pronunciation: {scores['pronunciation']:.1f}")
            print(f"    - Grammar: {scores['grammar']:.1f}")
            print(f"    - Vocabulary: {scores['vocabulary']:.1f}")
            print(f"    - Coherence: {scores['coherence']:.1f}")
        print()
    
    print("✅ Test completed!")
    print("\n" + "=" * 70)
    print("Key Differences vs. Old Python Rules:")
    print("=" * 70)
    print("✓ Understands context and meaning (not just patterns)")
    print("✓ Real grammar analysis (not regex-based)")
    print("✓ Evaluates pronunciation real issues")
    print("✓ Consistent with TOEIC standards")
    print("✓ Provides intelligent scoring\n")


if __name__ == "__main__":
    test_mistral_evaluation()
