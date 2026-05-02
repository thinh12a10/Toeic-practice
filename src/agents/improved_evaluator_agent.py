"""
IMPROVED Response Evaluator for TOEIC Speaking
Implements hybrid evaluation: LLM + Rule-based scoring

Key Improvements:
1. Better prompts for Mistral (task-specific)
2. Word-level analysis (your rule: full text = 5 points + deductions)
3. Speech similarity scoring (phonetic matching)
4. RAG-ready (reference response comparison)
"""

from typing import Dict, Any, Optional, List, Tuple
import os
import requests
from urllib.parse import urljoin
from difflib import SequenceMatcher
import re


class ImprovedResponseEvaluator:
    """
    Hybrid evaluator combining LLM + rule-based scoring
    
    Features:
    - Better prompts for consistent Mistral evaluation
    - Word-level comparison (finds missing/mispronounced words)
    - Phonetic similarity scoring
    - Reference text comparison
    """
    
    def __init__(self):
        """Initialize evaluator with Ollama connection"""
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.connected = False
        self.last_evaluation = None
        
        # Your scoring rules
        self.FULL_TEXT_BASE_SCORE = 5.0  # Full text = 5 points
        self.MAX_BONUS_POINTS = 5.0      # Can get 5 more points
        self.DEDUCTION_PER_WORD = 0.3    # Deduct 0.3 for each missed word
        
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
                print(f"✓ Improved Evaluator: Connected to Ollama ({self.ollama_model})")
            else:
                print(f"⚠ Evaluator: Ollama not responding (status {response.status_code})")
        except:
            print(f"⚠ Evaluator: Cannot connect to Ollama at {self.ollama_host}")
    
    def evaluate(
        self,
        user_response: str,
        question: Dict[str, Any],
        user_level: str = "intermediate"
    ) -> float:
        """
        IMPROVED: Hybrid evaluation using both LLM and rule-based scoring
        
        Your rules implemented:
        - Base score: 5 points if reader reads all text without missing major words
        - Remaining score: deducted based on missed/mispronounced words
        
        Args:
            user_response: User's text response
            question: Question dict with task details
            user_level: User's proficiency level
        
        Returns:
            float: Score from 0-10
        """
        if not user_response or len(user_response.strip()) == 0:
            return 0.0
        
        if not self.connected:
            print("⚠ Evaluator: Ollama not connected, using rule-based scoring only")
            return self._rule_based_evaluation(user_response, question)
        
        # Get both LLM and rule-based scores
        llm_score = self._get_llm_evaluation(user_response, question, user_level)
        rule_score = self._rule_based_evaluation(user_response, question)
        
        # Hybrid: weight both (60% LLM + 40% rule-based for your specific task)
        task_type = question.get("task_type", "read_aloud")
        
        if task_type == "read_aloud":
            # For read_aloud, your rules are more important (60% rules, 40% LLM)
            combined_score = (rule_score * 0.60) + (llm_score * 0.40)
        else:
            # For other tasks, keep original weights
            combined_score = (llm_score * 0.70) + (rule_score * 0.30)
        
        return min(10.0, max(0.0, combined_score))
    
    def _rule_based_evaluation(
        self,
        user_response: str,
        question: Dict[str, Any]
    ) -> float:
        """
        YOUR RULES: Word-level comparison
        
        Rules:
        1. Base = 5 points if full text is read (minor variations OK)
        2. Calculate word similarity and missed words
        3. Deduct for pronunciation errors (mispronounced words)
        4. Bonus for perfect or near-perfect match
        
        Args:
            user_response: User's response
            question: Question with original text
        
        Returns:
            float: Score 0-10 based on your rules
        """
        original_text = question.get("text", "")
        task_type = question.get("task_type", "respond")
        
        if task_type != "read_aloud":
            # For other task types, return neutral score
            return 5.0
        
        # Step 1: Word-level analysis
        original_words = self._normalize_text(original_text).split()
        response_words = self._normalize_text(user_response).split()
        
        # Step 2: Calculate text coverage
        text_coverage = self._calculate_text_coverage(original_words, response_words)
        
        # Step 3: Find missing and mispronounced words
        missing_words, mispronounced_words = self._analyze_differences(
            original_words, response_words
        )
        
        # Step 4: Calculate score using your rules
        score = self.FULL_TEXT_BASE_SCORE  # Start with 5
        
        # If user read everything correctly, add bonus
        if len(missing_words) == 0 and text_coverage >= 0.95:
            score += self.MAX_BONUS_POINTS  # 5 + 5 = 10 (perfect)
        else:
            # Deduct for missed words
            deduction = len(missing_words) * self.DEDUCTION_PER_WORD
            
            # Deduct for mispronounced words (half deduction)
            deduction += len(mispronounced_words) * (self.DEDUCTION_PER_WORD / 2)
            
            # Add bonus for good coverage (up to 5 points)
            bonus = text_coverage * self.MAX_BONUS_POINTS
            bonus -= deduction
            
            score += bonus
        
        return min(10.0, max(0.0, score))
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation (but keep spaces)
        text = re.sub(r'[.,!?;:\'"—–]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _calculate_text_coverage(
        self,
        original_words: List[str],
        response_words: List[str]
    ) -> float:
        """
        Calculate what percentage of original text was covered
        
        Returns: 0.0 to 1.0 (0% to 100%)
        """
        if not original_words:
            return 0.0
        
        # Use sequence matching to find covered words
        matcher = SequenceMatcher(None, original_words, response_words)
        matching_blocks = matcher.get_matching_blocks()
        
        covered_count = sum(block.size for block in matching_blocks)
        coverage = covered_count / len(original_words)
        
        return min(1.0, coverage)
    
    def _analyze_differences(
        self,
        original_words: List[str],
        response_words: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Find missing and mispronounced words
        
        Returns:
            (missing_words, mispronounced_words)
        """
        missing = []
        mispronounced = []
        
        response_set = set(response_words)
        
        for i, original_word in enumerate(original_words):
            # Check if word exists in response
            if original_word not in response_set:
                # Check for similar words (phonetic similarity)
                similar_word = self._find_similar_word(original_word, response_words)
                
                if similar_word:
                    # Similar but mispronounced
                    mispronounced.append(original_word)
                else:
                    # Missing entirely
                    missing.append(original_word)
        
        return missing, mispronounced
    
    def _find_similar_word(
        self,
        word: str,
        word_list: List[str],
        threshold: float = 0.7
    ) -> Optional[str]:
        """Find similar word in list (phonetic similarity)"""
        for candidate in word_list:
            ratio = SequenceMatcher(None, word, candidate).ratio()
            if ratio >= threshold:
                return candidate
        return None
    
    def _get_llm_evaluation(
        self,
        user_response: str,
        question: Dict[str, Any],
        user_level: str
    ) -> float:
        """
        IMPROVED PROMPT: Get evaluation from Mistral with better prompts
        
        Key improvements:
        1. Task-specific instructions
        2. Emphasize reading accuracy (for read_aloud tasks)
        3. Clear scoring criteria
        4. Examples for calibration
        """
        
        original_text = question.get("text", "")
        task_type = question.get("task_type", "read_aloud")
        
        # Build IMPROVED prompt based on task type
        if task_type == "read_aloud":
            prompt = self._build_read_aloud_prompt(
                user_response, original_text, user_level
            )
        else:
            prompt = self._build_general_prompt(
                user_response, question, user_level
            )
        
        try:
            response = requests.post(
                urljoin(self.ollama_host, "/api/generate"),
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,  # Lower for consistency
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 200,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "").strip()
                score = self._parse_llm_score(llm_response)
                return score
            else:
                return 5.0
                
        except Exception as e:
            print(f"⚠ LLM evaluation failed: {e}")
            return 5.0
    
    def _build_read_aloud_prompt(
        self,
        user_response: str,
        original_text: str,
        user_level: str
    ) -> str:
        """IMPROVED: Prompt specifically for read-aloud tasks"""
        return f"""You are a TOEIC Speaking test expert evaluating a READ ALOUD task.

ORIGINAL TEXT TO READ:
"{original_text}"

USER'S RESPONSE:
"{user_response}"

USER LEVEL: {user_level}

For READ ALOUD tasks, evaluate ONLY these factors:
1. **Completeness** (0-10): Did they read the full text? Penalize heavily for missing words.
2. **Pronunciation Clarity** (0-10): Are words pronounced clearly and accurately?
3. **Pace & Fluency** (0-10): Natural pacing, no excessive hesitations?

SCORING RULES FOR READ ALOUD:
- Full text read correctly → 9-10
- Full text with minor mispronunciations → 7-8
- Text incomplete or many errors → Below 7

Respond with ONLY this format:
COMPLETENESS: [0-10]
PRONUNCIATION: [0-10]
FLUENCY: [0-10]
FINAL_SCORE: [0-10]"""
    
    def _build_general_prompt(
        self,
        user_response: str,
        question: Dict[str, Any],
        user_level: str
    ) -> str:
        """IMPROVED: General prompt for other task types"""
        task_type = question.get("task_type", "respond")
        
        return f"""You are a TOEIC Speaking test expert. Evaluate this response precisely.

TASK TYPE: {task_type}
USER LEVEL: {user_level}
USER'S RESPONSE:
"{user_response}"

Evaluate on scale 0-10:
1. **Relevance** (0-10): Does response answer the question?
2. **Grammar** (0-10): Is it grammatically correct?
3. **Vocabulary** (0-10): Is vocabulary appropriate for {user_level} level?
4. **Clarity** (0-10): Is it clear and understandable?

Respond with ONLY:
RELEVANCE: [0-10]
GRAMMAR: [0-10]
VOCABULARY: [0-10]
CLARITY: [0-10]
FINAL_SCORE: [0-10]"""
    
    def _parse_llm_score(self, response: str) -> float:
        """Extract final score from LLM response"""
        try:
            lines = response.split('\n')
            for line in lines:
                if 'FINAL_SCORE:' in line.upper():
                    score_text = line.split(':')[1].strip().split()[0]
                    return min(10.0, max(0.0, float(score_text)))
            
            # Fallback: extract any number
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                return min(10.0, max(0.0, float(numbers[-1])))
            
            return 5.0
        except:
            return 5.0
    
    def get_detailed_feedback(self, user_response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed breakdown of the evaluation
        
        Returns:
            Dict with detailed analysis including:
            - Missing words
            - Mispronounced words
            - Coverage percentage
            - Improvement suggestions
        """
        original_text = question.get("text", "")
        
        original_words = self._normalize_text(original_text).split()
        response_words = self._normalize_text(user_response).split()
        
        coverage = self._calculate_text_coverage(original_words, response_words)
        missing, mispronounced = self._analyze_differences(original_words, response_words)
        
        return {
            "text_coverage": f"{coverage*100:.1f}%",
            "missing_words": missing,
            "mispronounced_words": mispronounced,
            "total_original_words": len(original_words),
            "words_read": len(response_words),
            "suggestions": self._generate_suggestions(missing, mispronounced)
        }
    
    def _generate_suggestions(self, missing: List[str], mispronounced: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if missing:
            suggestions.append(f"Missing {len(missing)} words: {', '.join(missing[:3])}")
        
        if mispronounced:
            suggestions.append(f"Watch pronunciation of: {', '.join(mispronounced[:3])}")
        
        if len(missing) + len(mispronounced) == 0:
            suggestions.append("Excellent! All words read correctly.")
        
        return suggestions
