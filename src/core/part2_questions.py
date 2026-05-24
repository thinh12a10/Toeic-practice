"""
Part 2 Question Engine for TOEIC Speaking Test
Part 2: Describe a Picture Task - Speaking to describe an image

Dynamic LLM-based generation using Gemini API
"""

from typing import Dict, Any, Optional
import random
import uuid
import os
from datetime import datetime
from google import genai


class Part2QuestionsEngine:
    """
    Generates TOEIC Speaking Part 2 questions (Describe a Picture task)
    
    Part 2 consists of:
    - 6-7 questions total
    - Each question is a picture description prompt
    - Preparation time: 10 seconds to read the prompt
    - Speaking time: 45 seconds to describe the picture
    - Focus on: Vocabulary, Grammar, Fluency, Organization
    """

    def __init__(self, level: str = "beginner", use_llm: bool = True):
        """
        Initialize Part 2 Question Engine
        
        Args:
            level: User level - 'beginner', 'intermediate', or 'advanced'
            use_llm: Whether to use LLM for dynamic generation (default True)
        """
        self.level = level
        self.questions_used = set()
        self.use_llm = use_llm
        self.llm_provider = None
        self.llm_client = None
        self.available_api = {
            "models/gemma-3-1b-it",
            "models/gemma-3-4b-it",
            "models/gemma-3-12b-it",
            "models/gemma-3-27b-it",
            "models/gemma-3n-e4b-it",
            "models/gemma-3n-e2b-it",
            "models/gemma-4-26b-a4b-it",
            "models/gemma-4-31b-it"
        }
        self.preferred_model = "models/gemma-4-31b-it"
        self.models_tried = set()
        
        # Initialize LLM client if requested
        if self.use_llm:
            self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize LLM client (Gemini)"""
        try:
            # Setup Gemini API if key is available (Google's LLM)
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.llm_provider = "gemini"
                self.llm_client = genai.Client(api_key=gemini_api_key)
                print("✓ Initialized Gemini API for dynamic question generation (Part 2)")
                return
        except Exception as e:
            print(f"⚠ Gemini API initialization failed: {e}")
        
        print("⚠ No API keys found, please check your GEMINI_API_KEY environment variable")

    def _generate_with_gemini(self) -> Optional[str]:
        """Generate a question using Gemini API with fallback models"""
        try:
            prompt = self._build_generation_prompt()
            
            # Create list of models to try: preferred first, then others
            models_to_try = [self.preferred_model]
            models_to_try.extend([m for m in self.available_api if m != self.preferred_model])
            
            # Try each model until one succeeds
            for model in models_to_try:
                if model in self.models_tried:
                    continue
                
                try:
                    self.models_tried.add(model)
                    print(f"⏳ Trying model: {model}")
                    
                    response = self.llm_client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    print(f"✓ Successfully generated with model: {model}")
                    return response.text.strip()
                    
                except Exception as e:
                    print(f"⚠ Model {model} failed: {e}")
                    continue
            
            print("⚠ All available models failed for generation")
            return None
            
        except Exception as e:
            print(f"⚠ Gemini generation failed: {e}")
            return None

    def _build_generation_prompt(self) -> str:
        """Build the prompt for LLM question generation"""
        difficulty_map = {
            "beginner": "simple and concrete (basic objects, clear actions, present tense, everyday vocabulary)",
            "intermediate": "moderately complex (multiple activities, varied tenses, some professional vocabulary, subtle details)",
            "advanced": "complex and nuanced (multiple layers of activity, advanced vocabulary, inferences required, professional/technical contexts)"
        }
        
        topics = [
            "office", "restaurant", "shopping mall", "park", "conference room", 
            "airport", "library", "manufacturing facility", "coffee shop", 
            "warehouse", "technology startup", "healthcare facility", "research lab",
            "corporate boardroom", "retail store", "public transportation"
        ]
        selected_topic = random.choice(topics)
        
        difficulty_description = difficulty_map.get(self.level, difficulty_map["beginner"])
        
        prompt = f"""Generate a single TOEIC Part 2 (Describe a Picture) practice question for {self.level} level students.

Requirements:
- Difficulty: {difficulty_description}
- Topic: {selected_topic}
- Format: A prompt asking student to describe a picture/scene
- Include 3-5 guiding questions to help structure the response
- Real-world business/professional context
- Appropriate for 45 seconds of continuous speaking
- Natural, clear English instruction
- Realistic and engaging scenario

The prompt should guide students to describe:
- What they see in the picture
- Who/what is present
- What activities are happening
- Any relevant details about the setting or atmosphere

Format your response EXACTLY like this (no markdown, just plain text):
[PROMPT] Your picture description prompt with guiding questions here
[TOPIC] topic_name
[DIFFICULTY] easy|medium|hard"""
        
        return prompt

    def _parse_llm_response(self, response: str) -> Optional[Dict[str, str]]:
        """Parse LLM response into structured format"""
        try:
            lines = response.strip().split("\n")
            parsed = {}
            
            for line in lines:
                if line.startswith("[PROMPT]"):
                    parsed["prompt"] = line.replace("[PROMPT]", "").strip()
                elif line.startswith("[TOPIC]"):
                    parsed["topic"] = line.replace("[TOPIC]", "").strip()
                elif line.startswith("[DIFFICULTY]"):
                    parsed["difficulty"] = line.replace("[DIFFICULTY]", "").strip()
            
            # Validate required fields
            if "prompt" not in parsed or not parsed["prompt"]:
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
        """Generate a question using LLM (Gemini)"""
        if not self.use_llm or not self.llm_provider:
            return None
        
        try:
            raw_response = self._generate_with_gemini()
            
            if not raw_response:
                return None
            
            parsed = self._parse_llm_response(raw_response)
            if not parsed:
                return None
            
            question = {
                "id": str(uuid.uuid4())[:8],
                "task_type": "describe_picture",
                "part": 2,
                "level": self.level,
                "prompt": parsed["prompt"],
                "topic": parsed.get("topic", "general"),
                "difficulty": parsed.get("difficulty", "medium"),
                "preparation_time": 10,
                "speaking_time": 45,
                "instruction": "Please describe the picture in detail. You have 45 seconds to speak.",
                "generated_by": self.llm_provider
            }
            
            return question
        except Exception as e:
            print(f"⚠ Dynamic generation failed: {e}")
            return None
    
    def generate_question(self) -> Dict[str, Any]:
        """
        Generate a Part 2 (Describe a Picture) question using LLM
        
        Returns:
            Dict with question details including:
            - id: Unique question identifier
            - task_type: Always "describe_picture" for Part 2
            - level: User level
            - prompt: Picture description prompt
            - topic: Question topic
            - difficulty: Question difficulty
            - preparation_time: Time to read prompt
            - speaking_time: Time to speak
            - instruction: Task instruction
            - generated_by: LLM provider name (gemini)
        """
        # Generate using LLM
        if self.use_llm:
            llm_question = self._generate_dynamic_question()
            if llm_question:
                return llm_question
        
        raise RuntimeError("LLM not available for question generation")
    
    def reset_session(self) -> None:
        """Reset question tracking and model attempts for new session"""
        self.questions_used.clear()
        self.models_tried.clear()
    
    def enable_llm(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM generation
        
        Args:
            enabled: Whether to enable LLM generation
        """
        self.use_llm = enabled
        if enabled:
            self._initialize_llm()
