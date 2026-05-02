"""
Dictionary Agent for TOEIC Speaking Test
Provides word definitions, IPA pronunciation, and Vietnamese meanings
Uses LLM with caching for efficient word lookups
"""

import json
import os
from typing import Dict, Optional, Any
from datetime import datetime
import requests
import re


class DictionaryAgent:
    """
    AI Agent for fetching word information including:
    - IPA (International Phonetic Alphabet)
    - Vietnamese meaning
    - Part of speech
    - Example usage
    """
    
    def __init__(self):
        """Initialize Dictionary Agent with caching"""
        self.cache_file = "word_cache.json"
        self.word_cache = self._load_cache()
        self.llm_provider = None
        self.llm_client = None
        self._initialize_llm()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load word cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save word cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.word_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _initialize_llm(self) -> None:
        """Initialize LLM client (Ollama > OpenAI > Anthropic)"""
        try:
            # Try Ollama first (local, free)
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                self.llm_provider = "ollama"
                print("✓ Dictionary Agent: Using Ollama (local)")
                return
        except:
            pass
        
        try:
            # Try OpenAI
            import openai
            if os.getenv("OPENAI_API_KEY"):
                self.llm_provider = "openai"
                self.llm_client = openai.OpenAI()
                print("✓ Dictionary Agent: Using OpenAI")
                return
        except:
            pass
        
        try:
            # Try Anthropic
            import anthropic
            if os.getenv("ANTHROPIC_API_KEY"):
                self.llm_provider = "anthropic"
                self.llm_client = anthropic.Anthropic()
                print("✓ Dictionary Agent: Using Anthropic Claude")
                return
        except:
            pass
        
        print("⚠ Dictionary Agent: No LLM provider available. Using fallback mode.")
    
    def get_word_info(self, word: str) -> Dict[str, Any]:
        """
        Get comprehensive word information including IPA and Vietnamese meaning
        
        Args:
            word: The word to lookup
            
        Returns:
            Dictionary with word information:
            {
                'word': str,
                'ipa': str,
                'pronunciation': str (description),
                'vietnamese_meaning': str,
                'definition': str,
                'part_of_speech': str,
                'example': str,
                'phonetic_symbols': str
            }
        """
        word_lower = word.lower().strip()
        
        # Check cache first
        if word_lower in self.word_cache:
            return self.word_cache[word_lower]
        
        # Fetch from LLM
        word_info = self._fetch_from_llm(word_lower)
        
        # Cache the result
        if word_info:
            self.word_cache[word_lower] = word_info
            self._save_cache()
        
        return word_info or self._get_default_response(word_lower)
    
    def _fetch_from_llm(self, word: str) -> Optional[Dict[str, Any]]:
        """Fetch word information from LLM"""
        if not self.llm_provider:
            return None
        
        prompt = self._build_prompt(word)
        
        try:
            if self.llm_provider == "ollama":
                return self._query_ollama(prompt)
            elif self.llm_provider == "openai":
                return self._query_openai(prompt)
            elif self.llm_provider == "anthropic":
                return self._query_anthropic(prompt)
        except Exception as e:
            print(f"Error fetching word info from LLM: {e}")
        
        return None
    
    def _build_prompt(self, word: str) -> str:
        """Build prompt for LLM to get word information"""
        return f"""Provide information about the English word "{word}" in JSON format with these exact fields:
{{
    "word": "{word}",
    "ipa": "[IPA symbols for pronunciation]",
    "pronunciation": "[brief description of how to pronounce, e.g., 'sounds like...']",
    "vietnamese_meaning": "[Vietnamese translation/meaning]",
    "definition": "[concise English definition]",
    "part_of_speech": "[noun/verb/adjective/etc]",
    "example": "[one example sentence using this word]",
    "phonetic_symbols": "[alternative phonetic representation if available]"
}}

Be accurate with IPA. For Vietnamese meaning, provide a clear translation that a Vietnamese speaker would understand. Return ONLY valid JSON."""
    
    def _query_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query Ollama LLM"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return self._parse_json_response(result.get("response", ""))
        except Exception as e:
            print(f"Ollama query error: {e}")
        
        return None
    
    def _query_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query OpenAI API"""
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a linguistics expert. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI query error: {e}")
        
        return None
    
    def _query_anthropic(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query Anthropic Claude"""
        try:
            response = self.llm_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return self._parse_json_response(response.content[0].text)
        except Exception as e:
            print(f"Anthropic query error: {e}")
        
        return None
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON in response (may contain extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
        except Exception as e:
            print(f"JSON parsing error: {e}")
        
        return None
    
    def _get_default_response(self, word: str) -> Dict[str, Any]:
        """Get default response when LLM is unavailable"""
        return {
            "word": word,
            "ipa": f"/{word}/",
            "pronunciation": f"Pronunciation guide not available - {word}",
            "vietnamese_meaning": "Không có dữ liệu",
            "definition": "Word definition not available. Enable an LLM provider for full info.",
            "part_of_speech": "unknown",
            "example": "No example available",
            "phonetic_symbols": "N/A"
        }
    
    def extract_words_from_text(self, text: str) -> list:
        """
        Extract words from text that are suitable for dictionary lookup
        Filters out articles, prepositions, etc.
        
        Args:
            text: Text to extract words from
            
        Returns:
            List of words (lowercase, unique)
        """
        # Common words to exclude
        stop_words = {
            'a', 'an', 'the', 'is', 'are', 'am', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            'of', 'in', 'on', 'at', 'by', 'to', 'from', 'for', 'with',
            'and', 'or', 'but', 'not', 'no', 'yes', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this',
            'that', 'these', 'those', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'as', 'if', 'then'
        }
        
        # Extract words (only alphabetic)
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter out stop words and return unique
        return list(set(w for w in words if w not in stop_words and len(w) > 2))
    
    def clear_cache(self):
        """Clear the word cache"""
        self.word_cache = {}
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except:
                pass
