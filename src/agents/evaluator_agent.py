from typing import Dict, Any, Optional
import os
import json

from google import genai
from google.genai import types


class ResponseEvaluator:
    """
    TOEIC Speaking Part 1 Evaluator
    """

    PRONUNCIATION_WEIGHT = 0.4
    INTONATION_WEIGHT = 0.3
    PAUSING_WEIGHT = 0.3

    def __init__(self):

        gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(
            api_key=gemini_api_key
        )

        self.available_models = [
            "models/gemini-2.5-flash",
            "models/gemini-2.5-flash-lite",
            "models/gemini-3.1-flash-lite-preview"
        ]
        self.preferred_model = "models/gemini-3.1-flash-lite-preview"
        self.models_tried = set()

        self.last_evaluation = None

    def evaluate(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        user_level: str = "intermediate"
    ) -> Dict[str, Any]:

        if not audio_bytes:
            return {
                "total_score": 0.0,
                "feedback": "No audio detected."
            }

        result = self._get_llm_evaluation(
            audio_bytes,
            user_response,
            question,
            user_level
        )

        if not result:
            return {
                "total_score": 0.0,
                "feedback": "Evaluation failed."
            }

        self.last_evaluation = result

        total_score = (
            result["pronunciation"]["score"] * self.PRONUNCIATION_WEIGHT +
            result["intonation"]["score"] * self.INTONATION_WEIGHT +
            result["pausing"]["score"] * self.PAUSING_WEIGHT
        )

        result["total_score"] = round(total_score, 1)

        return result

    def _get_llm_evaluation(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        user_level: str
    ) -> Optional[Dict[str, Any]]:

        original_text = question.get("text", "")

        prompt = f"""
You are a professional TOEIC Speaking evaluator.

Evaluate the AUDIO only.

ORIGINAL TEXT:
{original_text}

USER TRANSCRIPT:
{user_response}

Evaluate:

1. Pronunciation
2. Intonation & Stress
3. Pausing / Phrasing

SCORING:
- 0 to 10
- Use decimal scores if needed

IMPORTANT:
- Return ONLY valid JSON
- Use double quotes
- No markdown
- No explanation outside JSON
"""

        response_schema = {
            "type": "object",
            "properties": {
                "pronunciation": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number"
                        },
                        "strengths": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "improvement_tips": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "score",
                        "strengths",
                        "issues",
                        "improvement_tips"
                    ]
                },

                "intonation": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number"
                        },
                        "strengths": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "improvement_tips": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "score",
                        "strengths",
                        "issues",
                        "improvement_tips"
                    ]
                },

                "pausing": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number"
                        },
                        "strengths": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "improvement_tips": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "score",
                        "strengths",
                        "issues",
                        "improvement_tips"
                    ]
                },

                "overall_feedback": {
                    "type": "string"
                }
            },

            "required": [
                "pronunciation",
                "intonation",
                "pausing",
                "overall_feedback"
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
                "pronunciation",
                "intonation",
                "pausing"
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

            print(f"⚠ Audio evaluation failed: {e}")

            try:
                print("RAW MODEL RESPONSE:")
                print(response.text)
            except:
                pass

            return None

    def reset_session(self) -> None:
        """Reset model attempts for new session"""
        self.models_tried.clear()