"""
Response Evaluator for TOEIC Speaking
Evaluates responses using Mistral LLM via Ollama (local inference)

Uses LLM-based evaluation for intelligent analysis of:
- Fluency (smoothness, pace, hesitations)
- Pronunciation (accuracy, clarity)
- Grammar (accuracy, variety)
- Vocabulary (appropriateness, range)
- Coherence (organization, task completion)

Score range: 0-10
"""

from typing import Dict, Any, Optional
import os
import requests
from urllib.parse import urljoin


class ResponseEvaluator:
    """
    Evaluates user responses using Mistral model via Ollama
    
    Features:
    - Intelligent LLM-based analysis
    - Local inference (no cloud APIs)
    - Fast and free evaluation
    - Provides detailed feedback
    """
    
    # Scoring rubric weights (for final calculation)
    FLUENCY_WEIGHT = 0.20
    PRONUNCIATION_WEIGHT = 0.20
    GRAMMAR_WEIGHT = 0.25
    VOCABULARY_WEIGHT = 0.20
    COHERENCE_WEIGHT = 0.15
    
    def __init__(self):
        """Initialize evaluator with Ollama connection"""
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.connected = False
        self.last_evaluation = None
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test connection to Ollama server"""
        try:
            response = requests.get(
                urljoin(self.ollama_host, "/api/tags"),
                timeout=3
            )
            if response.status_code == 200:
                self.connected = True
                print(f"✓ Evaluator: Connected to Ollama ({self.ollama_model})")
            else:
                print(f"⚠ Evaluator: Ollama not responding (status {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"⚠ Evaluator: Cannot connect to Ollama at {self.ollama_host}")
        except Exception as e:
            print(f"⚠ Evaluator: Connection test failed: {e}")
    
    def evaluate(
        self,
        user_response: str,
        question: Dict[str, Any],
        user_level: str = "intermediate"
    ) -> float:
        """
        Evaluate a user response using Mistral LLM
        
        Args:
            user_response: User's text response
            question: Question dict with task details
            user_level: User's proficiency level ('beginner', 'intermediate', 'advanced')
        
        Returns:
            float: Score from 0-10
        """
        if not user_response or len(user_response.strip()) == 0:
            return 0.0
        
        if not self.connected:
            print("⚠ Evaluator: Ollama not connected, cannot evaluate")
            return 5.0  # Default neutral score
        
        # Get evaluation from Mistral
        scores_dict = self._get_llm_evaluation(user_response, question, user_level)
        
        if not scores_dict:
            print("⚠ Evaluator: Failed to get evaluation from LLM")
            return 5.0  # Default neutral score
        
        # Store for feedback generation
        self.last_evaluation = scores_dict
        
        # Calculate weighted average
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
        user_response: str,
        question: Dict[str, Any],
        user_level: str
    ) -> Optional[Dict[str, float]]:
        """
        Get evaluation scores from Mistral LLM via Ollama
        
        Args:
            user_response: User's response text
            question: Question details
            user_level: User's proficiency level
        
        Returns:
            Dict with scores for [fluency, pronunciation, grammar, vocabulary, coherence]
            or None if evaluation fails
        """
        
        # Build the evaluation prompt
        original_text = question.get("text", "")
        task_type = question.get("task_type", "read_aloud")
        
        prompt = f"""You are an expert TOEIC Speaking test evaluator. Evaluate this response precisely.

ORIGINAL TEXT TO READ:
"{original_text}"

USER'S RESPONSE:
"{user_response}"

USER LEVEL: {user_level}
TASK TYPE: {task_type}

Evaluate these 5 criteria on a scale of 0-10:
1. **Fluency**: How smooth and natural is the speech? (consider pacing, hesitations)
2. **Pronunciation**: How clearly are words pronounced? (accuracy and clarity)
3. **Grammar**: How grammatically correct is the response?
4. **Vocabulary**: Is vocabulary appropriate for the {user_level} level?
5. **Coherence**: Does the response complete the task properly?

IMPORTANT: Respond with ONLY these 5 lines, nothing else:
FLUENCY: [number 0-10]
PRONUNCIATION: [number 0-10]
GRAMMAR: [number 0-10]
VOCABULARY: [number 0-10]
COHERENCE: [number 0-10]"""

        try:
            response = requests.post(
                urljoin(self.ollama_host, "/api/generate"),
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Low temperature for consistent scoring
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 256,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "").strip()
                
                # Parse the response
                scores = self._parse_evaluation_response(llm_response)
                return scores
            else:
                print(f"⚠ Ollama error: Status {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("⚠ Ollama not running. Make sure to start it with: ollama serve")
            self.connected = False
            return None
        except requests.exceptions.Timeout:
            print("⚠ Ollama evaluation timed out")
            return None
        except Exception as e:
            print(f"⚠ LLM evaluation failed: {e}")
            return None
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, float]:
        """
        Parse LLM response to extract individual scores
        
        Expected format:
        FLUENCY: 8
        PRONUNCIATION: 7
        GRAMMAR: 9
        VOCABULARY: 8
        COHERENCE: 7
        """
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
                line = line.strip()
                if not line:
                    continue
                
                # Parse each scoring line
                if 'FLUENCY:' in line.upper():
                    try:
                        score = float(line.split(':')[1].strip().split()[0])
                        scores['fluency'] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        pass
                
                elif 'PRONUNCIATION:' in line.upper():
                    try:
                        score = float(line.split(':')[1].strip().split()[0])
                        scores['pronunciation'] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        pass
                
                elif 'GRAMMAR:' in line.upper():
                    try:
                        score = float(line.split(':')[1].strip().split()[0])
                        scores['grammar'] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        pass
                
                elif 'VOCABULARY:' in line.upper():
                    try:
                        score = float(line.split(':')[1].strip().split()[0])
                        scores['vocabulary'] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        pass
                
                elif 'COHERENCE:' in line.upper():
                    try:
                        score = float(line.split(':')[1].strip().split()[0])
                        scores['coherence'] = min(10.0, max(0.0, score))
                    except (ValueError, IndexError):
                        pass
            
            return scores
            
        except Exception as e:
            print(f"⚠ Failed to parse evaluation response: {e}")
            return scores
