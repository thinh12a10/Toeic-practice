"""
Question Engine for TOEIC Speaking Practice
Generates contextual TOEIC-style speaking questions
"""

from typing import Dict, List, Any
import random
import uuid


class QuestionEngine:
    """
    Generates TOEIC Speaking practice questions
    
    Supports 6 main TOEIC task types:
    1. Read aloud
    2. Repeat a sentence
    3. Say a sentence based on picture
    4. Respond to question (open-ended)
    5. Read information and respond
    6. Express opinion
    """
    
    # Sample question database by difficulty level
    QUESTIONS_BY_LEVEL = {
        "beginner": {
            "read_aloud": [
                {"text": "Hello, my name is John.", "topic": "greeting"},
                {"text": "I like to play basketball on weekends.", "topic": "hobby"},
                {"text": "The weather is nice today.", "topic": "weather"},
                {"text": "I work in a big company downtown.", "topic": "work"},
            ],
            "repeat": [
                {"original": "Could you please send me the report?", "topic": "business"},
                {"original": "I have a meeting at two o'clock.", "topic": "schedule"},
                {"original": "The product is available in three colors.", "topic": "product"},
            ],
            "respond": [
                {"question": "What do you do for work?", "topic": "work"},
                {"question": "How do you spend your free time?", "topic": "hobby"},
                {"question": "Where are you from?", "topic": "personal"},
            ],
            "opinion": [
                {"prompt": "Do you prefer working in an office or at home?", "topic": "work"},
                {"prompt": "What is your favorite season?", "topic": "nature"},
            ],
        },
        "intermediate": {
            "read_aloud": [
                {"text": "Our quarterly sales have increased by 15% compared to last year.", "topic": "business"},
                {"text": "The conference will cover topics ranging from technology to environmental sustainability.", "topic": "event"},
                {"text": "Customer satisfaction surveys indicate a 92% approval rating for our new product line.", "topic": "business"},
            ],
            "repeat": [
                {"original": "We should prioritize quality over quantity in this project.", "topic": "business"},
                {"original": "The research demonstrates significant correlation between sleep and productivity.", "topic": "science"},
            ],
            "respond": [
                {"question": "Can you describe your experience with project management?", "topic": "work"},
                {"question": "What strategies do you use to manage your time effectively?", "topic": "time_management"},
            ],
            "opinion": [
                {"prompt": "What role should artificial intelligence play in the workplace?", "topic": "technology"},
                {"prompt": "How important is work-life balance for career success?", "topic": "work"},
            ],
        },
        "advanced": {
            "read_aloud": [
                {"text": "Organizational resilience fundamentally depends on cultivating a culture of innovation and continuous improvement.", "topic": "management"},
                {"text": "The implications of digital transformation transcend operational efficiency, fundamentally reshaping business models and value propositions.", "topic": "technology"},
            ],
            "repeat": [
                {"original": "Strategic stakeholder engagement necessitates multifaceted communication protocols and sophisticated relationship management.", "topic": "business"},
                {"original": "The proliferation of remote work paradigms requires substantial organizational restructuring and reimagined collaboration frameworks.", "topic": "work"},
            ],
            "respond": [
                {"question": "How would you approach implementing a major organizational restructuring?", "topic": "management"},
                {"question": "What factors should companies consider when expanding into emerging markets?", "topic": "business"},
            ],
            "opinion": [
                {"prompt": "How will artificial intelligence reshape the nature of work and employment in the next decade?", "topic": "technology"},
                {"prompt": "What is the balance between corporate social responsibility and profitability?", "topic": "ethics"},
            ],
        }
    }
    
    def __init__(self, level: str = "intermediate"):
        """
        Initialize question engine
        
        Args:
            level: User level - 'beginner', 'intermediate', or 'advanced'
        """
        self.level = level
        self.questions_used = set()
    
    def generate_question(self) -> Dict[str, Any]:
        """
        Generate a random TOEIC-style question appropriate for user level
        
        Returns:
            Dict with question details
        """
        task_types = ["read_aloud", "repeat", "respond", "opinion"]
        task_type = random.choice(task_types)
        
        questions = self.QUESTIONS_BY_LEVEL.get(self.level, self.QUESTIONS_BY_LEVEL["intermediate"])
        
        if task_type not in questions or not questions[task_type]:
            task_type = "respond"  # fallback
        
        question_data = random.choice(questions[task_type])
        
        question = {
            "id": str(uuid.uuid4())[:8],
            "task_type": task_type,
            "level": self.level,
            "topic": question_data.get("topic", "general"),
        }
        
        # Add task-specific fields
        if task_type == "read_aloud":
            question["instruction"] = "Please read the following text aloud:"
            question["text"] = question_data["text"]
            question["expected_length"] = "short"  # ~20-30 seconds
        
        elif task_type == "repeat":
            question["instruction"] = "Listen and repeat the following sentence:"
            question["original_text"] = question_data["original"]
            question["expected_length"] = "short"  # ~10-15 seconds
        
        elif task_type == "respond":
            question["instruction"] = "Please respond to the following question:"
            question["question_text"] = question_data["question"]
            question["expected_length"] = "medium"  # ~30-45 seconds
        
        elif task_type == "opinion":
            question["instruction"] = "Please share your opinion on the following:"
            question["prompt_text"] = question_data["prompt"]
            question["expected_length"] = "medium"  # ~45-60 seconds
        
        return question
    
    def get_question_count(self) -> int:
        """Get number of questions used in current session"""
        return len(self.questions_used)
    
    def reset_session(self) -> None:
        """Reset question tracking for new session"""
        self.questions_used.clear()
