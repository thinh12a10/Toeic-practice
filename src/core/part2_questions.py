"""
Part 2 Question Engine for TOEIC Speaking Test
Part 2: Repeat Task - Listening and repeating spoken text
"""

from typing import List, Dict, Any, Optional
import random
import uuid
from datetime import datetime

class Part2QuestionsEngine:
    """
    Generates TOEIC Speaking Part 2 questions (Repeat task)
    
    Part 2 consists of:
    - 6-7 questions total
    - Each question là một câu tiếng Anh được phát âm
    - 15 giây để nghe
    - 15 giây để lặp lại
    - Focus on: Listening, Pronunciation, Intonation
    """

    def __init__(self, level: str = "beginner"):
        self.level = level
        self.questions_used = set()
        self.questions_db = self._initialize_questions()

    def _initialize_questions(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize câu hỏi cho Part 2 theo level"""
        return {
            "beginner": [
                {"text": "Could you please send me the report by tomorrow?", "topic": "business"},
                {"text": "I have a meeting at two o'clock this afternoon.", "topic": "schedule"},
                {"text": "The product is available in three different colors.", "topic": "product"},
                {"text": "Thank you for your help with this project.", "topic": "gratitude"},
                {"text": "Would you like to join us for lunch?", "topic": "social"},
                {"text": "Please remember to lock the door before leaving.", "topic": "reminder"},
                {"text": "The new office building opens next month.", "topic": "news"},
            ],
            "intermediate": [
                {"text": "We should prioritize quality over quantity in this project.", "topic": "business"},
                {"text": "The research demonstrates significant correlation between sleep and productivity.", "topic": "science"},
                {"text": "Customer feedback indicates we need to improve our response time.", "topic": "business"},
                {"text": "I recommend implementing this strategy starting next quarter.", "topic": "management"},
                {"text": "The conference will feature keynote speakers from leading tech companies.", "topic": "event"},
                {"text": "Could you clarify the budget requirements for the marketing campaign?", "topic": "business"},
            ],
            "advanced": [
                {"text": "Strategic stakeholder engagement necessitates multifaceted communication protocols.", "topic": "business"},
                {"text": "The implications of digital transformation transcend operational efficiency.", "topic": "technology"},
                {"text": "Organizational resilience fundamentally depends on cultivating innovation culture.", "topic": "management"},
                {"text": "We should explore synergistic opportunities that align with our core competencies.", "topic": "strategy"},
            ],
        }
    
    def generate_question(self) -> Optional[Dict[str, Any]]:
        """Generate a new question for Part 2"""
        if len(self.questions_used) >= len(self.questions_db.get(self.level, [])):
            self.questions_used.clear()
        
        available = [
            q for q in self.questions_db.get(self.level, [])
            if q["text"] not in self.questions_used
        ]

        if not available:
            return {"text": "Could not generate question", "topic": "error"}
        question = random.choice(available)
        self.questions_used.add(question["text"])

        return {
            "id": str(uuid.uuid4())[:8],
            "text": question["text"],
            "topic": question["topic"],
            "part": 2,
            "difficulty": self.level,
            "listening_time": 15,
            "repeat_time": 15,
            "generated_at": datetime.now().isoformat()
        }
