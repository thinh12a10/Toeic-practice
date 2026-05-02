"""
Feedback Generator for TOEIC Speaking
Provides constructive feedback and improvement suggestions
"""

from typing import Dict, Any
import re


class FeedbackGenerator:
    """
    Generates personalized feedback on TOEIC Speaking responses
    Includes:
    - Strengths
    - Areas for improvement
    - Specific suggestions
    - Next steps
    """
    
    def __init__(self):
        """Initialize feedback generator"""
        self.feedback_templates = self._load_templates()
    
    def generate_feedback(
        self,
        user_response: str,
        question: Dict[str, Any],
        score: float
    ) -> str:
        """
        Generate comprehensive feedback for a response
        
        Args:
            user_response: User's response text
            question: Question details
            score: Score from evaluator (0-10)
        
        Returns:
            str: Detailed feedback
        """
        feedback_parts = []
        
        # Add score feedback
        score_feedback = self._generate_score_feedback(score)
        feedback_parts.append(score_feedback)
        
        # Add task-specific feedback
        task_feedback = self._generate_task_feedback(user_response, question, score)
        feedback_parts.append(task_feedback)
        
        # Add improvement suggestions
        suggestions = self._generate_suggestions(user_response, score)
        if suggestions:
            feedback_parts.append(suggestions)
        
        return "\n".join(feedback_parts)
    
    def _generate_score_feedback(self, score: float) -> str:
        """Generate feedback based on score"""
        if score >= 9.0:
            return "Excellent! Your response was very strong. 🌟"
        elif score >= 8.0:
            return "Very good work! Your response showed solid command. 👍"
        elif score >= 7.0:
            return "Good effort! You demonstrated understanding of the task. 💪"
        elif score >= 5.0:
            return "Fair attempt. There's room for improvement. 📈"
        elif score >= 3.0:
            return "You captured some elements, but focus on the key improvements below. ⚠️"
        else:
            return "This response needs significant work. Review the suggestions carefully. 📝"
    
    def _generate_task_feedback(
        self,
        response: str,
        question: Dict[str, Any],
        score: float
    ) -> str:
        """Generate task-specific feedback"""
        task_type = question.get("task_type", "respond")
        feedback_lines = []
        
        words = response.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', response)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Task-specific analysis
        feedback_lines.append("\n📌 Task Analysis:")
        
        if task_type == "read_aloud":
            if word_count < 15:
                feedback_lines.append("- Response is too short. Try to read the full text clearly.")
            else:
                feedback_lines.append("- You covered the main text well.")
            
            if score >= 7:
                feedback_lines.append("- Your reading was clear and at good pace.")
        
        elif task_type == "repeat":
            if word_count < 5:
                feedback_lines.append("- Make sure to repeat the full sentence accurately.")
            else:
                feedback_lines.append("- Good attempt at repeating the sentence structure.")
        
        elif task_type == "respond":
            if sentence_count < 2:
                feedback_lines.append("- Expand your answer with more complete sentences.")
            elif sentence_count >= 3:
                feedback_lines.append("- Excellent! You provided a detailed multi-part response.")
            
            if word_count < 30:
                feedback_lines.append("- Try speaking for 30-45 seconds; provide more detail.")
        
        elif task_type == "opinion":
            if not self._has_opinion_marker(response):
                feedback_lines.append("- Clearly state your opinion (e.g., 'I think', 'I believe').")
            else:
                feedback_lines.append("- Good: You clearly expressed your opinion.")
            
            if sentence_count < 2:
                feedback_lines.append("- Add reasons or examples to support your opinion.")
        
        # Grammar feedback
        if self._has_common_errors(response):
            feedback_lines.append("- Watch for grammatical errors (see 'Common Issues' section).")
        else:
            feedback_lines.append("- Your grammar is accurate!")
        
        return "\n".join(feedback_lines)
    
    def _generate_suggestions(self, response: str, score: float) -> str:
        """Generate specific improvement suggestions"""
        suggestions = []
        suggestions.append("\n💡 Specific Improvements:")
        
        words = response.split()
        word_count = len(words)
        
        # Length suggestions
        if word_count < 25:
            suggestions.append("1. Speak longer: Aim for 30-60 second responses depending on task type.")
        
        # Vocabulary suggestions
        unique_words = len(set(w.lower() for w in words))
        diversity = unique_words / max(1, word_count)
        if diversity < 0.5:
            suggestions.append("2. Expand vocabulary: Use more varied words instead of repeating the same ones.")
        
        # Sentence structure suggestions
        sentences = re.split(r'[.!?]+', response)
        sentence_count = len([s for s in sentences if s.strip()])
        if sentence_count < 2:
            suggestions.append("3. Use varied sentence structures (statements, questions, complex sentences).")
        
        # Common errors
        errors = self._find_common_errors(response)
        if errors:
            suggestions.append(f"4. Grammar issues found: {', '.join(errors[:2])}")
        
        # Fluency suggestion
        if score < 7:
            suggestions.append("5. Practice speaking naturally: Slow down and avoid long pauses.")
        
        suggestions.append("\n📚 Next Steps:")
        suggestions.append("- Listen to native speaker examples of similar questions")
        suggestions.append("- Record yourself and compare to the model answer")
        suggestions.append("- Try this question again after reviewing the feedback")
        
        return "\n".join(suggestions)
    
    def _has_opinion_marker(self, response: str) -> bool:
        """Check if response contains opinion markers"""
        opinion_markers = [
            "think", "believe", "opinion", "agree", "disagree", 
            "prefer", "consider", "view", "feel", "seem"
        ]
        return any(marker in response.lower() for marker in opinion_markers)
    
    def _has_common_errors(self, response: str) -> bool:
        """Check for common grammatical errors"""
        common_error_patterns = [
            r"\bare\s+\w+\s+are\b",  # double are
            r"\bis\s+\w+\s+is\b",    # double is
            r"\bwas\s+you\b",        # subject-verb agreement
            r"\bwere\s+he\b",        # subject-verb agreement
        ]
        
        for pattern in common_error_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        
        return False
    
    def _find_common_errors(self, response: str) -> list:
        """Find specific common errors in response"""
        errors = []
        
        if re.search(r"\bare\s+\w+\s+are\b", response, re.IGNORECASE):
            errors.append("double 'are'")
        
        if re.search(r"\bis\s+\w+\s+is\b", response, re.IGNORECASE):
            errors.append("double 'is'")
        
        if re.search(r"\bwas\s+you\b", response, re.IGNORECASE):
            errors.append("'was' with 'you' (use 'were')")
        
        if re.search(r"\bwere\s+he\b", response, re.IGNORECASE):
            errors.append("'were' with 'he' (use 'was')")
        
        if re.search(r"\bdon't\s+\w+s\b", response, re.IGNORECASE):
            errors.append("verb disagreement with negative")
        
        return errors
    
    def _load_templates(self) -> Dict[str, str]:
        """Load feedback templates"""
        return {
            "excellent": "Excellent! Your response demonstrated mastery of the task.",
            "good": "Good response. You addressed the key points.",
            "fair": "Fair effort. Work on the areas mentioned above.",
            "needs_work": "This response needs more development.",
        }
