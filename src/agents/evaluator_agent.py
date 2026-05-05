from typing import Dict, Any, Optional
import os
from google import genai
from google.genai import types


class ResponseEvaluator:
    """
    Evaluates user responses using Gemini Audio Model

    - Uses REAL audio for pronunciation & fluency
    - Uses transcript for grammar/vocab support
    """

    FLUENCY_WEIGHT = 0.20
    PRONUNCIATION_WEIGHT = 0.20
    GRAMMAR_WEIGHT = 0.25
    VOCABULARY_WEIGHT = 0.20
    COHERENCE_WEIGHT = 0.15

    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=gemini_api_key)
        self.last_evaluation = None

    def evaluate(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        user_level: str = "intermediate"
    ) -> float:

        if not audio_bytes:
            return 0.0

        scores_dict = self._get_llm_evaluation(
            audio_bytes,
            user_response,
            question,
            user_level
        )

        if not scores_dict:
            print("⚠ Evaluator: fallback score used")
            return 5.0

        self.last_evaluation = scores_dict

        total_score = (
            (scores_dict.get('fluency', 5.0) * self.FLUENCY_WEIGHT) +
            (scores_dict.get('grammar', 5.0) * self.GRAMMAR_WEIGHT) +
            (scores_dict.get('vocabulary', 5.0) * self.VOCABULARY_WEIGHT) +
            (scores_dict.get('coherence', 5.0) * self.COHERENCE_WEIGHT) +
            (scores_dict.get('pronunciation', 5.0) * self.PRONUNCIATION_WEIGHT)
        )

        return min(10.0, max(0.0, total_score))

    def _get_llm_evaluation(
        self,
        audio_bytes: bytes,
        user_response: str,
        question: Dict[str, Any],
        user_level: str
    ) -> Optional[Dict[str, float]]:

        original_text = question.get("text", "")
        task_type = question.get("task_type", "read_aloud")

        prompt = f"""
    You are an expert TOEIC Speaking evaluator.

    TASK: {task_type}
    LEVEL: {user_level}

    ORIGINAL TEXT:
    {original_text}

    USER TRANSCRIPT:
    {user_response}

    IMPORTANT:
    - Evaluate using the AUDIO primarily
    - Compare with ORIGINAL TEXT
    - Penalize missing or incorrect words

    Score from 0-10:

    FLUENCY:
    PRONUNCIATION:
    GRAMMAR:
    VOCABULARY:
    COHERENCE:

    Return ONLY:
    FLUENCY: X
    PRONUNCIATION: X
    GRAMMAR: X
    VOCABULARY: X
    COHERENCE: X
    """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # ✅ FIXED MODEL
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )

            llm_response = response.text.strip()

            return self._parse_evaluation_response(llm_response)

        except Exception as e:
            print(f"⚠ Audio evaluation failed: {e}")
            return None
    def _parse_evaluation_response(self, response: str) -> Dict[str, float]:
        scores = {
            'fluency': 5.0,
            'pronunciation': 5.0,
            'grammar': 5.0,
            'vocabulary': 5.0,
            'coherence': 5.0
        }

        try:
            lines = response.split('\n')

            for line in lines:
                line = line.strip().upper()

                def extract_value(text):
                    try:
                        return float(text.split(":")[1].strip().split()[0])
                    except:
                        return None

                if "FLUENCY:" in line:
                    val = extract_value(line)
                    if val is not None:
                        scores['fluency'] = min(10, max(0, val))

                elif "PRONUNCIATION:" in line:
                    val = extract_value(line)
                    if val is not None:
                        scores['pronunciation'] = min(10, max(0, val))

                elif "GRAMMAR:" in line:
                    val = extract_value(line)
                    if val is not None:
                        scores['grammar'] = min(10, max(0, val))

                elif "VOCABULARY:" in line:
                    val = extract_value(line)
                    if val is not None:
                        scores['vocabulary'] = min(10, max(0, val))

                elif "COHERENCE:" in line:
                    val = extract_value(line)
                    if val is not None:
                        scores['coherence'] = min(10, max(0, val))

            return scores

        except Exception as e:
            print(f"⚠ Parse error: {e}")
            return scores