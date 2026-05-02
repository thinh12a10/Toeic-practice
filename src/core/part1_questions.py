"""
Part 1 Question Engine for TOEIC Speaking Test
Part 1: Read Aloud Task

Dynamic LLM-based generation using Ollama, OpenAI, or Anthropic
"""

from typing import Dict, Any, Optional
import random
import uuid
import json
import os
from datetime import datetime
import requests
from urllib.parse import urljoin
from google import genai


class Part1QuestionEngine:
    """
    Generates TOEIC Speaking Part 1 questions (Read Aloud task type)
    
    Part 1 consists of:
    - 6 questions total
    - Each question is a sentence or short passage
    - 45 seconds to read each one
    - Focus on pronunciation, fluency, and intonation
    """
    
    def __init__(self, level: str = "beginner", use_llm: bool = True):
        """
        Initialize Part 1 Question Engine
        
        Args:
            level: User level - 'beginner', 'intermediate', or 'advanced'
            use_llm: Whether to use LLM for dynamic generation (default True)
        """
        self.level = level
        self.questions_used = set()
        self.use_llm = use_llm
        self.llm_provider = None
        self.llm_client = None
        
        # Initialize LLM client if requested
        if self.use_llm:
            self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize LLM client (Gemini > Ollama)"""
        try:
            # Try Gemini API first (Google's LLM, free tier available with Google account)
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.llm_provider = "gemini"
                self.llm_client = genai.Client(api_key=gemini_api_key)
                print("✓ Initialized Gemini API for dynamic question generation")
                return
        except Exception as e:
            print(f"⚠ Gemini API initialization failed: {e}")

        try:
            # Try Ollama first (local, free)
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
            
            # Test connection to Ollama
            response = requests.get(urljoin(ollama_host, "/api/tags"), timeout=2)
            if response.status_code == 200:
                self.llm_provider = "ollama"
                self.llm_client = {
                    "host": ollama_host,
                    "model": ollama_model
                }
                print(f"✓ Initialized Ollama ({ollama_model}) for dynamic question generation")
                return
        except Exception as e:
            print(f"⚠ Ollama connection failed: {e}")
            print(f"  (Make sure Ollama is running: ollama serve)")
        
        print("⚠ No LLM available (Ollama not running, no API keys found).")
        raise RuntimeError("No LLM provider available. Please ensure Ollama is running or API keys are configured.")
    
    def _generate_with_ollama(self) -> Optional[str]:
        """Generate a question using Ollama (local inference)"""
        try:
            prompt = self._build_generation_prompt()
            host = self.llm_client["host"]
            model = self.llm_client["model"]
            
            response = requests.post(
                urljoin(host, "/api/generate"),
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 256,  # Limit output tokens for faster generation
                },
                timeout=120  # Longer timeout for local inference
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"⚠ Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("⚠ Ollama connection failed. Make sure Ollama is running with: ollama serve")
            return None
        except Exception as e:
            print(f"⚠ Ollama generation failed: {e}")
            return None
    
    def _generate_with_gemini(self) -> Optional[str]:
        """Generate a question using Gemini API (Google's LLM)"""
        try:
            prompt = self._build_generation_prompt()
            response = self.llm_client.models.generate_content(
                model="models/gemma-3-12b-it",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠ Gemini generation failed: {e}")
            return None
    
    def _build_generation_prompt(self) -> str:
        """Build the prompt for LLM question generation"""
        difficulty_map = {
            "beginner": "simple, everyday English (present tense, basic vocabulary, clear sentence structure)",
            "intermediate": "moderate complexity (varied tenses, professional/business vocabulary, multiple clauses)",
            "advanced": "complex, sophisticated English (technical/domain-specific vocabulary, varied structures, nuanced content)"
        }
        
        topics = ["work", "hobby", "family", "travel", "food", "technology", "health", "education", "environment", "sports"]
        selected_topic = random.choice(topics)
        
        difficulty_description = difficulty_map.get(self.level, difficulty_map["beginner"])
        
        prompt = f"""Generate a single TOEIC Part 1 (Read Aloud) practice question for {self.level} level students.

Requirements:
- Difficulty: {difficulty_description}
- Topic: {selected_topic}
- Length: 2-4 sentences (approximately 60-120 words) - MUST be substantial enough for 45-60 seconds of reading
- Real-world context that English learners might encounter
- Natural, grammatically correct English
- Include varied sentence structures and transitions
- Appropriate for 45-60 seconds of reading aloud (not rushed)
- No pronunciation marks or special characters

Format your response EXACTLY like this (no markdown, just plain text):
[QUESTION] Your question text here
[TOPIC] topic_name
[DIFFICULTY] easy|medium|hard"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into structured format"""
        try:
            lines = response.strip().split("\n")
            parsed = {}
            
            for line in lines:
                if line.startswith("[QUESTION]"):
                    parsed["text"] = line.replace("[QUESTION]", "").strip()
                elif line.startswith("[TOPIC]"):
                    parsed["topic"] = line.replace("[TOPIC]", "").strip()
                elif line.startswith("[DIFFICULTY]"):
                    parsed["difficulty"] = line.replace("[DIFFICULTY]", "").strip()
            
            # Validate required fields
            if "text" not in parsed or not parsed["text"]:
                return None
            
            if "topic" not in parsed:
                parsed["topic"] = "general"
            
            if "difficulty" not in parsed:
                parsed["difficulty"] = "medium"
            
            return parsed
        except Exception as e:
            print(f"⚠ Failed to parse LLM response: {e}")
            return None
    
    def _generate_dynamic_question(self) -> Optional[Dict[str, Any]]:
        """Generate a question using LLM (tries Gemini > Ollama)"""
        if not self.use_llm or not self.llm_provider:
            return None
        
        try:
            # Try to generate based on provider priority
            raw_response = None
            
            if self.llm_provider == "ollama":
                raw_response = self._generate_with_ollama()
            elif self.llm_provider == "gemini":
                raw_response = self._generate_with_gemini()
            
            if not raw_response:
                return None
            
            parsed = self._parse_llm_response(raw_response)
            if not parsed:
                return None
            
            question = {
                "id": str(uuid.uuid4())[:8],
                "task_type": "read_aloud",
                "part": 1,
                "level": self.level,
                "text": parsed["text"],
                "topic": parsed.get("topic", "general"),
                "difficulty": parsed.get("difficulty", "medium"),
                "instruction": "Please read the following text aloud:",
                "expected_length": "45 seconds",
                "generated_by": self.llm_provider
            }
            
            return question
        except Exception as e:
            print(f"⚠ Dynamic generation failed: {e}")
            return None
    

    def generate_question(self) -> Dict[str, Any]:
        """
        Generate a Part 1 (Read Aloud) question using LLM
        
        Returns:
            Dict with question details including:
            - id: Unique question identifier
            - task_type: Always "read_aloud" for Part 1
            - level: User level
            - text: Text to read aloud
            - topic: Question topic
            - difficulty: Question difficulty
            - instruction: Task instruction
            - expected_length: Expected speaking time
            - generated_by: LLM provider name (ollama, openai, or anthropic)
        """
        # Generate using LLM
        if self.use_llm:
            llm_question = self._generate_dynamic_question()
            if llm_question:
                return llm_question
        
        raise RuntimeError("LLM not available for question generation")
    
    def get_part1_sequence(self, num_questions: int = 6) -> list:
        """
        Generate a sequence of Part 1 questions (typically 6)
        
        Args:
            num_questions: Number of questions to generate (default 6)
        
        Returns:
            List of question dictionaries
        """
        questions = []
        for _ in range(num_questions):
            questions.append(self.generate_question())
        return questions
    
    def get_questions_used_count(self) -> int:
        """Get number of questions used in current session"""
        return len(self.questions_used)
    
    def reset_session(self) -> None:
        """Reset question tracking for new session"""
        self.questions_used.clear()
    
    def get_generation_source(self) -> str:
        """
        Get the current question generation source
        
        Returns:
            LLM provider name (ollama, openai, or anthropic)
        """
        if self.use_llm and self.llm_provider:
            return self.llm_provider
        return "unknown"
    
    def enable_llm(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM generation
        
        Args:
            enabled: Whether to enable LLM generation
        """
        self.use_llm = enabled
        if enabled:
            self._initialize_llm()
