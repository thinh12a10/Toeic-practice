"""
Core TOEIC Speaking Practice AI Agent
Manages conversation state, question delivery, and response handling
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class UserProfile:
    """User profile for tracking progress"""
    user_id: str
    name: str
    level: str = "beginner"  # beginner, intermediate, advanced
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Response:
    """User response to a question"""
    question_id: str
    user_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    score: Optional[float] = None
    feedback: Optional[str] = None


@dataclass
class SessionState:
    """Current session state"""
    session_id: str
    user_profile: UserProfile
    current_question_id: Optional[str] = None
    responses: List[Response] = field(default_factory=list)
    total_score: float = 0.0
    question_count: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    
    def add_response(self, response: Response) -> None:
        """Add a response to session history"""
        self.responses.append(response)
        if response.score is not None:
            self.total_score += response.score
            self.question_count += 1
    
    def get_average_score(self) -> float:
        """Calculate average score for session"""
        if self.question_count == 0:
            return 0.0
        return self.total_score / self.question_count


class TOEICSpeakingAgent:
    """
    AI Agent for TOEIC Speaking practice
    
    Manages:
    - Conversation state and session tracking
    - Question generation and delivery
    - Response processing and evaluation
    - Feedback and score reporting
    """
    
    def __init__(self, user_profile: UserProfile):
        """
        Initialize the agent with user profile
        
        Args:
            user_profile: UserProfile object containing user information
        """
        self.user_profile = user_profile
        self.session: Optional[SessionState] = None
        self.question_bank: Dict[str, Any] = {}
        self.current_question: Optional[Dict[str, Any]] = None
    
    def start_session(self) -> SessionState:
        """
        Start a new practice session
        
        Returns:
            SessionState: New session object
        """
        from datetime import datetime
        import uuid
        
        session_id = str(uuid.uuid4())[:8]
        self.session = SessionState(
            session_id=session_id,
            user_profile=self.user_profile
        )
        print(f"✓ Session started: {session_id}")
        return self.session
    
    def end_session(self) -> Dict[str, Any]:
        """
        End current session and return summary
        
        Returns:
            Dict with session summary including scores and stats
        """
        if self.session is None:
            raise RuntimeError("No active session")
        
        summary = {
            "session_id": self.session.session_id,
            "duration_seconds": (datetime.now() - self.session.started_at).total_seconds(),
            "questions_answered": self.session.question_count,
            "average_score": self.session.get_average_score(),
            "total_score": self.session.total_score,
            "responses": len(self.session.responses)
        }
        
        print(f"\n✓ Session ended")
        print(f"  Questions answered: {summary['questions_answered']}")
        print(f"  Average score: {summary['average_score']:.2f}/10")
        
        return summary
    
    def get_next_question(self) -> Dict[str, Any]:
        """
        Retrieve the next question
        
        Returns:
            Dict with question details (id, text, task_type, etc.)
        """
        # Import here to avoid circular dependency
        from src.core.questions import QuestionEngine
        
        if self.session is None:
            raise RuntimeError("No active session")
        
        engine = QuestionEngine(self.user_profile.level)
        question = engine.generate_question()
        
        self.current_question = question
        self.session.current_question_id = question["id"]
        
        return question
    
    def process_response(self, user_response_text: str) -> Response:
        """
        Process and evaluate user response
        
        Args:
            user_response_text: User's spoken/typed response
        
        Returns:
            Response object with score and feedback
        """
        # Import here to avoid circular dependency
        from src.agents.evaluator_agent import ResponseEvaluator
        from src.core.feedback import FeedbackGenerator
        
        if self.session is None or self.current_question is None:
            raise RuntimeError("No active question in session")
        
        # Create response object
        response = Response(
            question_id=self.current_question["id"],
            user_text=user_response_text
        )
        
        # Evaluate response
        evaluator = ResponseEvaluator()
        score = evaluator.evaluate(
            user_response=user_response_text,
            question=self.current_question,
            user_level=self.user_profile.level
        )
        response.score = score
        
        # Generate feedback
        feedback_gen = FeedbackGenerator()
        feedback = feedback_gen.generate_feedback(
            user_response=user_response_text,
            question=self.current_question,
            score=score
        )
        response.feedback = feedback
        
        # Add to session
        self.session.add_response(response)
        
        return response
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if self.session is None:
            raise RuntimeError("No active session")
        
        return {
            "session_id": self.session.session_id,
            "questions_answered": self.session.question_count,
            "average_score": self.session.get_average_score(),
            "total_score": self.session.total_score
        }
