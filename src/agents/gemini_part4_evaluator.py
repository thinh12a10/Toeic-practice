"""
TOEIC Speaking Part 4 Evaluator - Gemini API
Specialized evaluator for Document-Based Question Answering using Gemini API

Part 4 consists of answering 3 questions based on a provided document:
- Question 8 (15s): Basic factual details
- Question 9 (15s): Specific details or confirmation  
- Question 10 (30s): List multiple items

Evaluates:
- Completeness and Accuracy: 40 points
- Fluency: 30 points
- Grammar & Vocabulary: 30 points
Total: 100 points per question
"""

from typing import Dict, Any, Optional
import os
import json

from google import genai
from google.genai import types


class GeminiPart4Evaluator:
    """
    TOEIC Speaking Part 4 Evaluator using Gemini API
    
    Evaluates answers to document-based questions (Part 4)
    
    Scoring Breakdown:
    - Completeness and Accuracy: 40 points (Did they answer correctly using document info?)
    - Fluency: 30 points (Clarity, pronunciation, natural speech)
    - Grammar & Vocabulary: 30 points (Correct grammar, appropriate word choice)
    Total: 100 points per answer
    """

    COMPLETENESS_WEIGHT = 0.40
    FLUENCY_WEIGHT = 0.30
    GRAMMAR_WEIGHT = 0.30

    def __init__(self):
        """Initialize Gemini API client for Part 4 evaluation"""
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
        document: str,
        question: Dict[str, Any],
        user_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Evaluate a Part 4 response using Gemini API
        
        Args:
            audio_bytes: Audio file in bytes
            user_response: Transcribed or provided response text
            document: The reference document the question is based on
            question: Question dict with 'text', 'number' (8/9/10), etc.
            user_level: User proficiency level (beginner, intermediate, advanced)
        
        Returns:
            Evaluation result with scores and feedback
        """

        if not audio_bytes:
            return {
                "total_score": 0.0,
                "percentage": 0,
                "feedback": "No audio detected.",
                "completeness": {"score": 0, "feedback": "No audio"},
                "fluency": {"score": 0, "feedback": "No audio"},
                "grammar": {"score": 0, "feedback": "No audio"}
            }

        result = self._get_llm_evaluation(
            audio_bytes,
            user_response,
            document,
            question,
            user_level
        )

        if not result:
            return {
                "total_score": 0.0,
                "percentage": 0,
                "feedback": "Evaluation failed.",
                "completeness": {"score": 0, "feedback": "Error"},
                "fluency": {"score": 0, "feedback": "Error"},
                "grammar": {"score": 0, "feedback": "Error"}
            }

        self.last_evaluation = result

        # Calculate weighted total score
        total_score = (
            result["completeness"]["score"] * self.COMPLETENESS_WEIGHT +
            result["fluency"]["score"] * self.FLUENCY_WEIGHT +
            result["grammar"]["score"] * self.GRAMMAR_WEIGHT
        )

        result["total_score"] = round(total_score, 1)
        result["percentage"] = round((total_score / 100) * 100)

        return result

    def _get_llm_evaluation(
        self,
        audio_bytes: bytes,
        user_response: str,
        document: str,
        question: Dict[str, Any],
        user_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get evaluation from Gemini API
        
        Args:
            audio_bytes: Audio bytes to analyze
            user_response: User's response text
            document: Reference document
            question: Question information
            user_level: User's proficiency level
        
        Returns:
            Structured evaluation or None if failed
        """

        question_text = question.get("text", "")
        question_number = question.get("number", 8)

        level_guidance = {
            "beginner": "Basic vocabulary and grammar, some hesitation acceptable",
            "intermediate": "Good vocabulary, mostly correct grammar, minor errors acceptable",
            "advanced": "Advanced vocabulary, sophisticated structures, near-native fluency expected"
        }

        level_context = level_guidance.get(user_level, level_guidance["intermediate"])

        evaluation_prompt = f"""
You are an expert TOEIC Speaking evaluator specializing in Part 4 (Document-Based Questions).

EVALUATION CRITERIA FOR USER LEVEL: {user_level}
{level_context}

REFERENCE DOCUMENT:
{document}

QUESTION {question_number}:
{question_text}

USER'S RESPONSE (from audio):
{user_response}

Evaluate the response on these 3 criteria:

1. COMPLETENESS AND ACCURACY (0-40 points):
   - Did the response correctly answer the question?
   - Does it use accurate information from the document?
   - Is the answer complete and relevant?
   - For Question 10: Are all items listed accurately?

2. FLUENCY (0-30 points):
   - Clarity of pronunciation
   - Natural pacing and rhythm
   - Minimal hesitation and pauses
   - Overall smoothness of delivery

3. GRAMMAR & VOCABULARY (0-30 points):
   - Correct sentence structure and grammar
   - Appropriate word choice
   - Professional and clear language
   - Correct use of tenses and articles

SCORING RULES:
- Be strict with advanced level
- Be lenient with beginners  
- Prioritize ACCURACY for Part 4 (most important)
- Deduct for incomplete or incorrect answers
- Give full points only for near-perfect responses
- For Question 10, all items must be listed

IMPORTANT:
- Return ONLY valid JSON
- Use double quotes
- No markdown or explanation outside JSON
- Provide constructive, specific feedback
"""

        response_schema = {
            "type": "object",
            "properties": {
                "completeness": {
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
                "grammar": {
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
                "completeness",
                "fluency",
                "grammar",
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
                            evaluation_prompt
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
                "completeness",
                "fluency",
                "grammar"
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
            print(f"⚠ Part 4 evaluation failed: {e}")

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
            responses: List of response dicts with audio_bytes, text, document, question
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
                document=resp_data.get("document", ""),
                question=resp_data.get("question", {}),
                user_level=user_level
            )

            evaluations.append(eval_result)
            if eval_result.get("total_score"):
                total_scores.append(eval_result["total_score"])

        # Calculate averages
        avg_total = sum(total_scores) / len(total_scores) if total_scores else 0

        return {
            "evaluations": evaluations,
            "summary": {
                "count": len(evaluations),
                "average_score": round(avg_total, 1),
                "average_percentage": round((avg_total / 100) * 100)
            }
        }
