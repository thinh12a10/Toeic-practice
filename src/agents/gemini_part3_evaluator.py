"""
TOEIC Speaking Part 3 Evaluator - Gemini API
Specialized evaluator for Questions & Response task using Gemini API

Evaluates:
- Vocabulary & Word Choice
- Grammar & Accuracy
- Fluency & Coherence
- Comprehension & Responsiveness
- Content Relevance to Scenario
"""

from typing import Dict, Any, Optional
import os
import json

from google import genai
from google.genai import types


class GeminiPart3Evaluator:
    """
    TOEIC Speaking Part 3 Evaluator using Gemini API
    
    Scoring Breakdown:
    - Vocabulary: 25 points
    - Grammar: 25 points
    - Fluency: 25 points
    - Comprehension: 15 points
    - Content Relevance: 10 points
    Total: 100 points
    """

    VOCABULARY_WEIGHT = 0.25
    GRAMMAR_WEIGHT = 0.25
    FLUENCY_WEIGHT = 0.25
    COMPREHENSION_WEIGHT = 0.15
    CONTENT_WEIGHT = 0.10

    def __init__(self):
        """Initialize Gemini API client for Part 3 evaluation"""
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=gemini_api_key)

        self.available_models = [
            "models/gemini-2.5-flash",
            "models/gemini-2.5-flash-lite",
            "models/gemini-3.1-flash-lite-preview"
        ]
        self.preferred_model = "models/gemini-2.5-flash"
        self.models_tried = set()

        self.last_evaluation = None

    def evaluate(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        scenario: str = "",
        user_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Evaluate a Part 3 response using Gemini API
        
        Args:
            audio_bytes: Audio file in bytes
            user_response: Transcribed or provided response text
            question: Question dict with 'text', 'scenario', etc.
            scenario: Scenario description for context
            user_level: User proficiency level (beginner, intermediate, advanced)
        
        Returns:
            Evaluation result with scores and feedback
        """

        if not audio_bytes:
            return {
                "total_score": 0.0,
                "percentage": 0,
                "feedback": "No audio detected.",
                "vocabulary": {"score": 0, "feedback": "No audio"},
                "grammar": {"score": 0, "feedback": "No audio"},
                "fluency": {"score": 0, "feedback": "No audio"},
                "comprehension": {"score": 0, "feedback": "No audio"},
                "content": {"score": 0, "feedback": "No audio"}
            }

        result = self._get_llm_evaluation(
            audio_bytes,
            user_response,
            question,
            scenario,
            user_level
        )

        if not result:
            return {
                "total_score": 0.0,
                "percentage": 0,
                "feedback": "Evaluation failed.",
                "vocabulary": {"score": 0, "feedback": "Error"},
                "grammar": {"score": 0, "feedback": "Error"},
                "fluency": {"score": 0, "feedback": "Error"},
                "comprehension": {"score": 0, "feedback": "Error"},
                "content": {"score": 0, "feedback": "Error"}
            }

        self.last_evaluation = result

        # Calculate weighted total score
        total_score = (
            result["vocabulary"]["score"] * self.VOCABULARY_WEIGHT +
            result["grammar"]["score"] * self.GRAMMAR_WEIGHT +
            result["fluency"]["score"] * self.FLUENCY_WEIGHT +
            result["comprehension"]["score"] * self.COMPREHENSION_WEIGHT +
            result["content"]["score"] * self.CONTENT_WEIGHT
        )

        result["total_score"] = round(total_score, 1)
        result["percentage"] = round((total_score / 100) * 100)

        return result

    def _get_llm_evaluation(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        scenario: str,
        user_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get evaluation from Gemini API
        
        Args:
            audio_bytes: Audio bytes to analyze
            user_response: User's response text
            question: Question information
            scenario: Scenario description
            user_level: User's proficiency level
        
        Returns:
            Structured evaluation or None if failed
        """

        question_text = question.get("text", "")

        level_guidance = {
            "beginner": "Basic vocabulary, simple structures, some pauses acceptable",
            "intermediate": "Good vocabulary range, mostly correct structures, minor errors acceptable",
            "advanced": "Advanced vocabulary, complex structures, near-native fluency expected"
        }

        level_context = level_guidance.get(user_level, level_guidance["intermediate"])

        prompt = f"""
You are an expert TOEIC Speaking evaluator specializing in Part 3 (Questions & Response).

EVALUATION CRITERIA FOR USER LEVEL: {user_level}
{level_context}

SCENARIO:
{scenario}

QUESTION:
{question_text}

USER'S RESPONSE (from audio):
{user_response}

Evaluate the response on these 5 criteria (each out of 25 points, except Content=10 and Comprehension=15):

1. VOCABULARY (0-25): 
   - Word choice appropriateness
   - Range of vocabulary
   - Use of scenario-relevant terms

2. GRAMMAR (0-25):
   - Sentence structure accuracy
   - Tense usage
   - Agreement and correctness

3. FLUENCY (0-25):
   - Smooth delivery
   - Pacing and rhythm
   - Naturalness of speech

4. COMPREHENSION (0-15):
   - Understanding of the question
   - Relevance to the prompt
   - Completeness of answer

5. CONTENT RELEVANCE (0-10):
   - How well response fits the scenario
   - Logical coherence
   - Appropriateness to context

SCORING RULES:
- Be strict with advanced level
- Be lenient with beginners
- Deduct for awkward phrasing, unnatural speech
- Give full points only for near-perfect responses
- Partial credit is acceptable

IMPORTANT:
- Return ONLY valid JSON
- Use double quotes
- No markdown or explanation outside JSON
- Provide constructive, specific feedback
"""

        response_schema = {
            "type": "object",
            "properties": {
                "vocabulary": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["score", "feedback"]
                },
                "grammar": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["score", "feedback"]
                },
                "fluency": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["score", "feedback"]
                },
                "comprehension": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["score", "feedback"]
                },
                "content": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["score", "feedback"]
                },
                "overall_feedback": {
                    "type": "string"
                },
                "improvement_tips": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": [
                "vocabulary",
                "grammar",
                "fluency",
                "comprehension",
                "content",
                "overall_feedback",
                "improvement_tips"
            ]
        }

        try:
            # Create list of models to try: preferred first, then others
            models_to_try = [self.preferred_model]
            models_to_try.extend([m for m in self.available_models if m != self.preferred_model])

            response = None

            # Try each model until one succeeds
            for model in models_to_try:
                if model in self.models_tried:
                    continue

                try:
                    self.models_tried.add(model)
                    print(f"⏳ Trying model: {model}")

                    response = self.client.models.generate_content(
                        model=model,
                        contents=[
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type="audio/wav"
                            ),
                            prompt
                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=2000,
                            response_mime_type="application/json",
                            response_schema=response_schema
                        )
                    )

                    print(f"✓ Successfully generated with model: {model}")
                    break

                except Exception as model_error:
                    print(f"⚠ Model {model} failed: {model_error}")
                    response = None
                    continue

            if response is None:
                print("⚠ All available models failed for evaluation")
                return None

            if not response.text:
                print("⚠ Empty model response")
                return None

            text = response.text.strip()

            try:
                result = json.loads(text)

            except json.JSONDecodeError as json_error:
                print(f"⚠ JSON parse failed: {json_error}")
                print("RAW MODEL RESPONSE:")
                print(text)
                return None

            # ============================================
            # VALIDATE REQUIRED FIELDS
            # ============================================

            required_sections = [
                "vocabulary",
                "grammar",
                "fluency",
                "comprehension",
                "content"
            ]

            for section in required_sections:
                if section not in result:
                    print(f"⚠ Missing section: {section}")
                    return None

                if "score" not in result[section]:
                    print(f"⚠ Missing score in: {section}")
                    return None

            return result

        except Exception as e:
            print(f"⚠ Part 3 evaluation failed: {e}")

            try:
                print("RAW MODEL RESPONSE:")
                print(response.text)
            except:
                pass

            return None

    def reset_session(self) -> None:
        """Reset model attempts for new session"""
        self.models_tried.clear()

    def evaluate_batch(
        self,
        responses: list[Dict[str, Any]],
        user_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Evaluate multiple responses and generate summary
        
        Args:
            responses: List of response dicts with audio_bytes, text, question, scenario
            user_level: User's proficiency level
        
        Returns:
            Summary evaluation with average scores
        """

        evaluations = []
        total_scores = []

        for resp_data in responses:
            eval_result = self.evaluate(
                audio_bytes=resp_data.get("audio_bytes", b""),
                user_response=resp_data.get("text", ""),
                question=resp_data.get("question", {}),
                scenario=resp_data.get("scenario", ""),
                user_level=user_level
            )

            evaluations.append(eval_result)
            total_scores.append(eval_result.get("total_score", 0))

        avg_score = sum(total_scores) / len(total_scores) if total_scores else 0

        return {
            "total_responses": len(responses),
            "evaluations": evaluations,
            "average_score": round(avg_score, 1),
            "average_percentage": round((avg_score / 100) * 100),
            "summary": f"Completed evaluation of {len(responses)} Part 3 response(s)"
        }
