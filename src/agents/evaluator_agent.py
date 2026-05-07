from typing import Dict, Any, Optional
import os
from google import genai
from google.genai import types


class ResponseEvaluator:
    """
    TOEIC Speaking Part 1 Evaluator (Read Aloud)

    Focus:
    - Pronunciation
    - Intonation & Stress
    - Pausing / Phrasing
    """

    PRONUNCIATION_WEIGHT = 0.4
    INTONATION_WEIGHT = 0.3
    PAUSING_WEIGHT = 0.3

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

        scores = self._get_llm_evaluation(
            audio_bytes,
            user_response,
            question,
            user_level
        )

        if not scores:
            print("⚠ Evaluator: fallback score used")
            return 5.0

        self.last_evaluation = scores

        total_score = (
            scores["pronunciation"] * self.PRONUNCIATION_WEIGHT +
            scores["intonation"] * self.INTONATION_WEIGHT +
            scores["pausing"] * self.PAUSING_WEIGHT
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

        prompt = f"""
You are an expert TOEIC Speaking Part 1 evaluator (Read Aloud).

Evaluate the AUDIO based on TOEIC criteria.

ORIGINAL TEXT:
{original_text}

USER TRANSCRIPT (may be imperfect):
{user_response}

Focus ONLY on these 3 criteria:

1. PRONUNCIATION (0-10)
- Sound accuracy
- Clarity of words
- Mispronounced sounds

2. INTONATION & STRESS (0-10)
- Natural rise/fall of voice
- Word stress
- Sentence rhythm

3. PAUSING / PHRASING (0-10)
- Natural pauses
- Chunking of phrases
- Smooth flow (not word-by-word)

IMPORTANT:
- Compare audio with ORIGINAL TEXT
- Penalize skipped or incorrect words
- Ignore grammar and vocabulary

Return ONLY:

PRONUNCIATION: X
INTONATION: X
PAUSING: X
"""

        try:
            response = self.client.models.generate_content(
                model="models/gemini-3.1-flash-lite-preview",
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
            return self._parse_response(llm_response)

        except Exception as e:
            print(f"⚠ Audio evaluation failed: {e}")
            return None

    def _parse_response(self, response: str) -> Dict[str, float]:
        scores = {
            "pronunciation": 0.0,
            "intonation": 0.0,
            "pausing": 0.0
        }

        try:
            lines = response.split("\n")

            for line in lines:
                line = line.strip().upper()

                def extract(line):
                    try:
                        return float(line.split(":")[1].strip().split()[0])
                    except:
                        return None

                if "PRONUNCIATION:" in line:
                    val = extract(line)
                    if val is not None:
                        print(f"Extracted Pronunciation Score: {val}")
                        scores["pronunciation"] = val

                elif "INTONATION:" in line:
                    val = extract(line)
                    if val is not None:
                        print(f"Extracted Intonation Score: {val}")
                        scores["intonation"] = val

                elif "PAUSING:" in line:
                    val = extract(line)
                    if val is not None:
                        print(f"Extracted Pausing Score: {val}")
                        scores["pausing"] = val

            return scores

        except Exception as e:
            print(f"⚠ Parse error: {e}")
            return scores