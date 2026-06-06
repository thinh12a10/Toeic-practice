"""
Part 3 Question Engine for TOEIC Speaking Test
Part 3: Questions & Response Task - Answering questions about a scenario

Dynamic LLM-based generation using Gemini API
"""

from typing import Dict, Any, Optional
import random
import uuid
import os
from datetime import datetime
from google import genai


class Part3QuestionsEngine:
    """
    Generates TOEIC Speaking Part 3 questions (Questions & Response task)
    
    Part 3 consists of:
    - 3 questions total
    - Each question asks student to respond to a specific scenario or prompt
    - Preparation time: 10 seconds per question
    - Speaking time: 15 seconds per question
    - Focus on: Vocabulary, Grammar, Fluency, Comprehension, Responsiveness
    """

    def __init__(self, level: str = "beginner", use_llm: bool = True):
        """
        Initialize Part 3 Question Engine
        
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
        
        # Fallback questions (static)
        self._initialize_fallback_questions()

    def _initialize_llm(self) -> None:
        """Initialize LLM client (Gemini)"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.llm_provider = "gemini"
                self.llm_client = genai.Client(api_key=gemini_api_key)
                print("✓ Initialized Gemini API for dynamic question generation (Part 3)")
                return
        except Exception as e:
            print(f"⚠ Gemini API initialization failed: {e}")
        
        print("⚠ No API keys found, will use static questions")

    def _initialize_fallback_questions(self) -> None:
        """Initialize fallback static questions for each level"""
        self.fallback_questions = {
            "beginner": [
                {
                    "id": "p3_b001",
                    "scenario": "You are at a café with a friend",
                    "questions": [
                        "What drink would you like to order?",
                        "Why did you choose to meet here?",
                        "What do you usually do after coffee?"
                    ]
                },
                {
                    "id": "p3_b002",
                    "scenario": "You are shopping for work clothes",
                    "questions": [
                        "What color do you prefer for work shirts?",
                        "Where do you usually buy your work clothes?",
                        "How important is the price when you shop?"
                    ]
                },
                {
                    "id": "p3_b003",
                    "scenario": "You are planning a team lunch",
                    "questions": [
                        "What type of restaurant would you choose?",
                        "How many people should attend?",
                        "What time is best for lunch?"
                    ]
                },
                {
                    "id": "p3_b004",
                    "scenario": "You are attending a company meeting",
                    "questions": [
                        "What topics do you want to discuss?",
                        "How long should the meeting last?",
                        "What time is best for the meeting?"
                    ]
                },
                {
                    "id": "p3_b005",
                    "scenario": "You are traveling for business",
                    "questions": [
                        "Which city would you like to visit?",
                        "How long should the trip be?",
                        "What should you bring on the trip?"
                    ]
                }
            ],
            "intermediate": [
                {
                    "id": "p3_i001",
                    "scenario": "You are planning a project presentation for executives",
                    "questions": [
                        "What presentation tools and techniques would you recommend?",
                        "How would you structure the information to keep executives engaged?",
                        "What potential challenges might arise and how would you address them?"
                    ]
                },
                {
                    "id": "p3_i002",
                    "scenario": "Your company is implementing new office software",
                    "questions": [
                        "What approach would you take to help employees transition smoothly?",
                        "What training methods would be most effective for different team members?",
                        "How would you measure the success of this implementation?"
                    ]
                },
                {
                    "id": "p3_i003",
                    "scenario": "You are opening a new branch office in another city",
                    "questions": [
                        "What factors would influence your choice of location?",
                        "How would you recruit and hire the initial team?",
                        "What strategies would you use to attract clients to the new branch?"
                    ]
                },
                {
                    "id": "p3_i004",
                    "scenario": "Your department needs to reduce costs while maintaining quality",
                    "questions": [
                        "What areas would you identify for potential cost reduction?",
                        "How would you communicate these changes to your team?",
                        "What metrics would you use to ensure quality is maintained?"
                    ]
                },
                {
                    "id": "p3_i005",
                    "scenario": "You are building a more collaborative workplace culture",
                    "questions": [
                        "What initiatives would you implement to improve teamwork?",
                        "How would you measure the effectiveness of these initiatives?",
                        "What challenges might you encounter in changing the culture?"
                    ]
                }
            ],
            "advanced": [
                {
                    "id": "p3_a001",
                    "scenario": "Your company is navigating through significant digital transformation",
                    "questions": [
                        "How would you develop a comprehensive strategy that addresses technological, organizational, and human factors?",
                        "What methodologies would you employ to ensure stakeholder alignment and minimize resistance to change?",
                        "How would you establish metrics to demonstrate ROI and the strategic value of this transformation?"
                    ]
                },
                {
                    "id": "p3_a002",
                    "scenario": "You are leading a global team across multiple time zones and cultures",
                    "questions": [
                        "What communication frameworks and protocols would you establish to ensure effective collaboration?",
                        "How would you navigate cultural differences to foster inclusive decision-making?",
                        "What strategies would you implement to maintain team cohesion and morale?"
                    ]
                },
                {
                    "id": "p3_a003",
                    "scenario": "Your organization is facing market disruption from emerging competitors",
                    "questions": [
                        "How would you conduct a competitive analysis and identify strategic opportunities?",
                        "What innovation initiatives would you prioritize to maintain competitive advantage?",
                        "How would you communicate the strategic pivot to investors and stakeholders?"
                    ]
                },
                {
                    "id": "p3_a004",
                    "scenario": "You are establishing sustainability initiatives in your organization",
                    "questions": [
                        "How would you balance sustainability goals with profitability and operational efficiency?",
                        "What stakeholder engagement strategy would you employ to drive organizational commitment?",
                        "What measurement and reporting mechanisms would demonstrate progress toward ESG objectives?"
                    ]
                },
                {
                    "id": "p3_a005",
                    "scenario": "You are managing a high-stakes merger and integration process",
                    "questions": [
                        "What due diligence processes would you implement to identify integration risks and opportunities?",
                        "How would you develop a comprehensive change management plan to align two distinct corporate cultures?",
                        "What timeline and milestones would you establish for successful integration?"
                    ]
                }
            ]
        }

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """
        Get next question
        
        Returns:
            Dictionary with question data or None if all questions used
        """
        # Try LLM generation first
        if self.use_llm and self.llm_provider:
            question = self._generate_dynamic_question()
            if question:
                return question
        
        # Fall back to static questions
        return self._get_fallback_question()

    def _get_fallback_question(self) -> Optional[Dict[str, Any]]:
        """Get a random fallback question from static pool"""
        try:
            fallback_set = self.fallback_questions.get(self.level, self.fallback_questions["beginner"])
            
            # Find unused questions
            available = [q for q in fallback_set if q["id"] not in self.questions_used]
            
            if not available:
                # Reset if all used
                self.questions_used.clear()
                available = fallback_set
            
            if not available:
                return None
            
            question_data = random.choice(available)
            self.questions_used.add(question_data["id"])
            
            return {
                "id": question_data["id"],
                "part": 3,
                "level": self.level,
                "task_type": "questions_response",
                "scenario": question_data["scenario"],
                "questions": question_data["questions"],
                "preparation_time": 10,
                "speaking_time": 15,
                "total_questions": 3,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠ Failed to get fallback question: {e}")
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
                "task_type": "questions_response",
                "part": 3,
                "level": self.level,
                "scenario": parsed.get("scenario", ""),
                "questions": parsed.get("questions", []),
                "preparation_time": 10,
                "speaking_time": 15,
                "total_questions": 3,
                "difficulty": parsed.get("difficulty", "medium"),
                "created_at": datetime.now().isoformat()
            }
            
            self.questions_used.add(question["id"])
            return question
            
        except Exception as e:
            print(f"⚠ Dynamic question generation failed: {e}")
            return None

    def _generate_with_gemini(self) -> Optional[str]:
        """Generate a question using Gemini API with fallback models"""
        try:
            prompt = self._build_generation_prompt()
            
            models_to_try = [self.preferred_model]
            models_to_try.extend([m for m in self.available_api if m != self.preferred_model])
            
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
            "beginner": "simple and concrete (everyday workplace situations, basic vocabulary, present/past tense, clear context)",
            "intermediate": "moderately complex (business scenarios, mixed tenses, professional vocabulary, some problem-solving required)",
            "advanced": "complex and nuanced (strategic scenarios, advanced vocabulary, critical thinking, executive-level topics)"
        }
        
        scenarios = [
            "office management", "project planning", "client relations", "employee training",
            "budget management", "team collaboration", "product launch", "customer service",
            "supplier relations", "quality assurance", "marketing strategy", "sales performance",
            "technology implementation", "workplace diversity", "productivity improvement",
            "crisis management", "strategic planning", "career development", "company expansion",
            "environmental responsibility"
        ]
        selected_scenario = random.choice(scenarios)
        
        difficulty_description = difficulty_map.get(self.level, difficulty_map["beginner"])
        
        prompt = f"""Generate a single TOEIC Part 3 (Questions & Response) practice question set for {self.level} level students.

Requirements:
- Difficulty: {difficulty_description}
- Scenario: {selected_scenario}
- Format: A business/workplace scenario followed by 3 specific questions
- Students answer 10 seconds to prepare, then 15 seconds to answer each question
- Natural, professional English context
- Realistic and engaging scenario
- Questions should test comprehension, opinion, and practical thinking

Create 3 distinct questions that:
1. First question: asks for a specific choice or recommendation
2. Second question: asks for reasoning or explanation
3. Third question: asks about implications or next steps

Format your response EXACTLY like this (no markdown, just plain text):
[SCENARIO] Workplace scenario description here (2-3 sentences)
[Q1] First question here
[Q2] Second question here
[Q3] Third question here
[DIFFICULTY] easy|medium|hard"""
        
        return prompt

    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response into structured format"""
        try:
            lines = response.strip().split("\n")
            parsed = {
                "scenario": "",
                "questions": [],
                "difficulty": "medium"
            }
            
            for line in lines:
                if line.startswith("[SCENARIO]"):
                    parsed["scenario"] = line.replace("[SCENARIO]", "").strip()
                elif line.startswith("[Q1]"):
                    parsed["questions"].append(line.replace("[Q1]", "").strip())
                elif line.startswith("[Q2]"):
                    parsed["questions"].append(line.replace("[Q2]", "").strip())
                elif line.startswith("[Q3]"):
                    parsed["questions"].append(line.replace("[Q3]", "").strip())
                elif line.startswith("[DIFFICULTY]"):
                    parsed["difficulty"] = line.replace("[DIFFICULTY]", "").strip()
            
            # Validate required fields
            if not parsed["scenario"] or len(parsed["questions"]) != 3:
                return None
            
            return parsed
        except Exception as e:
            print(f"⚠ Failed to parse LLM response: {e}")
            return None

    def reset_questions(self) -> None:
        """Reset the questions used set to allow repeating questions"""
        self.questions_used.clear()
        self.models_tried.clear()
