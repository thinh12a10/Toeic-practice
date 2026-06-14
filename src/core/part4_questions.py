"""
Part 4 Question Engine for TOEIC Speaking Test
Part 4: Document-Based Question Answering (Questions 8, 9, 10)

Generates documents (schedules, itineraries, invoices, etc.) and questions about them.
Students have 45 seconds to read the document, then answer 3 questions:
- Question 8 (15s): Basic factual details
- Question 9 (15s): Specific details / confirmation
- Question 10 (30s): List multiple items

Dynamic LLM-based generation using Gemini API
"""

from typing import Dict, Any, Optional
import random
import uuid
import os
from datetime import datetime
from google import genai


class Part4QuestionsEngine:
    """
    Generates TOEIC Speaking Part 4 documents and questions
    
    Part 4 consists of:
    - 1 document (schedule, itinerary, invoice, conference program, etc.)
    - 3 questions to answer based on the document
    - Preparation time: 45 seconds (to read and understand the document)
    - Question 8: 15 seconds (basic factual details)
    - Question 9: 15 seconds (specific details or confirmation)
    - Question 10: 30 seconds (list multiple related items)
    - Focus on: Accuracy, Completeness, Fluency, Grammar, Vocabulary
    """

    def __init__(self, level: str = "beginner", use_llm: bool = True):
        """
        Initialize Part 4 Question Engine
        
        Args:
            level: User level - 'beginner', 'intermediate', or 'advanced'
            use_llm: Whether to use LLM for dynamic generation (default True)
        """
        self.level = level
        self.documents_used = set()
        self.use_llm = use_llm
        self.llm_provider = None
        self.llm_client = None
        self.available_api = {
            "models/gemma-3-1b-it",
            "models/gemma-3-4b-it",
            "models/gemma-3-12b-it",
            "models/gemma-3-27b-it",
            "models/gemma-3n-e4b-it",
            "models/gemma-3n-e2b-it",
            "models/gemma-4-26b-a4b-it",
            "models/gemma-4-31b-it"
        }
        self.preferred_model = "models/gemma-4-31b-it"
        self.models_tried = set()
        
        # Initialize LLM client if requested
        if self.use_llm:
            self._initialize_llm()
        
        # Fallback documents and questions (static)
        self._initialize_fallback_documents()

    def _initialize_llm(self) -> None:
        """Initialize LLM client (Gemini)"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.llm_provider = "gemini"
                self.llm_client = genai.Client(api_key=gemini_api_key)
                print("✓ Initialized Gemini API for dynamic question generation (Part 4)")
                return
        except Exception as e:
            print(f"⚠ Gemini API initialization failed: {e}")
        
        print("⚠ No API keys found, will use static questions")

    def _initialize_fallback_documents(self) -> None:
        """Initialize fallback static documents and questions for each level"""
        self.fallback_documents = {
            "beginner": [
                {
                    "id": "p4_b001",
                    "document_type": "Conference Schedule",
                    "document": """ANNUAL TECHNOLOGY CONFERENCE 2024
                    
Monday, June 17
9:00 AM - 10:00 AM    | Opening Keynote (Main Hall)
10:15 AM - 11:15 AM   | Workshop A: Cloud Computing (Room 201)
10:15 AM - 11:15 AM   | Workshop B: AI Basics (Room 202)
11:30 AM - 12:30 PM   | Lunch Break
1:00 PM - 2:00 PM     | Workshop C: Data Security (Room 203)
2:15 PM - 3:15 PM     | Panel Discussion (Main Hall)
3:30 PM - 4:30 PM     | Networking Reception (Lobby)""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "What time does the Opening Keynote start?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "Which workshop is in Room 202?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "Please list all the workshops offered in the morning session.",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                },
                {
                    "id": "p4_b002",
                    "document_type": "Meeting Agenda",
                    "document": """PROJECT KICKOFF MEETING
Meeting Date: Tuesday, July 2, 2024
Location: Conference Room B
Time: 2:00 PM - 3:30 PM

Attendees: Sarah (Project Manager), Tom (Developer), Lisa (Designer), Mike (QA)

Agenda:
2:00 - 2:10 PM    | Project Overview
2:10 - 2:30 PM    | Requirements Discussion
2:30 - 3:00 PM    | Timeline and Milestones
3:00 - 3:20 PM    | Team Responsibilities
3:20 - 3:30 PM    | Q&A and Next Steps""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "Where is the meeting being held?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "How many minutes will be spent on Requirements Discussion?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "Can you name all four attendees of this meeting?",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                },
                {
                    "id": "p4_b003",
                    "document_type": "Employee Handbook - Leave Policy",
                    "document": """COMPANY LEAVE POLICY

Vacation Days: 15 days per year
- Full-time employees receive 15 paid vacation days annually
- Must be requested at least 2 weeks in advance
- Maximum 5 consecutive days without manager approval

Sick Leave: 10 days per year
- Employees are entitled to 10 paid sick days
- Doctor's note required for absences over 3 consecutive days

Holidays: 10 public holidays
- New Year's Day, Independence Day, Thanksgiving, Christmas, etc.
- These are paid days off for all employees

Parental Leave: 12 weeks
- Applies to both mothers and fathers
- Contact HR for specific requirements""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "How many vacation days do full-time employees get each year?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "When is a doctor's note required for sick leave?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "List all the types of leave mentioned in this policy.",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                }
            ],
            "intermediate": [
                {
                    "id": "p4_i001",
                    "document_type": "Project Timeline",
                    "document": """Q3 2024 PRODUCT LAUNCH ROADMAP

Phase 1: Planning & Design (July 1 - July 31)
- Requirements gathering: July 1-10
- UI/UX design: July 8-24
- Technical architecture: July 15-28
- Design review: July 29-31

Phase 2: Development (August 1 - September 15)
- Backend development: August 1 - September 5
- Frontend development: August 5 - September 8
- Integration testing: August 20 - September 12
- Bug fixes: September 10-15

Phase 3: Launch Preparation (September 16 - October 5)
- User acceptance testing: September 16-25
- Documentation: September 16-30
- Training sessions: October 1-3
- Go-live: October 5""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "When does the UI/UX design phase end?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "Which activities occur during Phase 2 that are not development?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "What are all the activities scheduled during the Launch Preparation phase?",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                },
                {
                    "id": "p4_i002",
                    "document_type": "Training Program Schedule",
                    "document": """PROFESSIONAL DEVELOPMENT PROGRAM - FALL 2024

Module 1: Leadership Skills (September 9-13)
Instructor: Dr. James Chen
Location: Building A, Room 301
Time: 9:00 AM - 12:00 PM
Cost: $500 per participant
Capacity: 25 students

Module 2: Advanced Excel (September 16-20)
Instructor: Maria Rodriguez
Location: Building B, Computer Lab 1
Time: 2:00 PM - 5:00 PM
Cost: $350 per participant
Capacity: 20 students

Module 3: Communication for Managers (September 23-27)
Instructor: Patricia Williams
Location: Building A, Room 305
Time: 10:00 AM - 1:00 PM
Cost: $450 per participant
Capacity: 30 students

All modules include lunch and materials.""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "Who is the instructor for the Leadership Skills module?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "Which two modules meet in Building A?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "List the cost and time schedule for all three modules.",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                }
            ],
            "advanced": [
                {
                    "id": "p4_a001",
                    "document_type": "Budget Allocation Report",
                    "document": """FISCAL YEAR 2024 DEPARTMENTAL BUDGET ALLOCATION

Operations Department: $2,450,000 (38% of total)
- Infrastructure & Maintenance: $1,200,000
- Equipment & Technology: $750,000
- Personnel & Training: $500,000

Marketing & Sales: $1,100,000 (17% of total)
- Digital Marketing: $600,000
- Events & Conferences: $300,000
- Sales Support: $200,000

Research & Development: $2,100,000 (33% of total)
- Product Innovation: $1,300,000
- Process Improvement: $600,000
- Patent Filing & IP Protection: $200,000

Human Resources & Administration: $620,000 (10% of total)
- Recruitment & Development: $350,000
- Compliance & Legal: $200,000
- Administrative Operations: $70,000

Total Annual Budget: $6,270,000""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "What is the total annual budget allocation?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "Which department receives the largest budget and what percentage does it represent?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "Describe all the budget allocations within the Research & Development department.",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                },
                {
                    "id": "p4_a002",
                    "document_type": "Supply Chain & Logistics",
                    "document": """INTERNATIONAL SHIPPING ROUTES & DELIVERY SCHEDULES - Q4 2024

Route A: Asia to North America
Port of Origin: Shanghai (China)
Port of Destination: Los Angeles (USA)
Departure Schedule: Every Monday & Thursday
Transit Time: 12-14 days
Capacity: 5,000 TEU (Twenty-foot Equivalent Units)
Cost per Unit: $850

Route B: Europe to North America
Port of Origin: Rotterdam (Netherlands)
Port of Destination: New York (USA)
Departure Schedule: Every Tuesday & Friday
Transit Time: 7-9 days
Capacity: 4,500 TEU
Cost per Unit: $750

Route C: Asia to Europe
Port of Origin: Shanghai (China)
Port of Destination: Hamburg (Germany)
Departure Schedule: Every Wednesday & Sunday
Transit Time: 35-40 days
Capacity: 6,000 TEU
Cost per Unit: $920

All shipments include customs clearance documentation.""",
                    "questions": [
                        {
                            "number": 8,
                            "text": "What is the transit time for shipments from Asia to North America?",
                            "time_limit": 15,
                            "type": "factual"
                        },
                        {
                            "number": 9,
                            "text": "Which route has the highest capacity and what is its cost per unit?",
                            "time_limit": 15,
                            "type": "specific"
                        },
                        {
                            "number": 10,
                            "text": "Provide complete departure schedules and transit times for all three routes.",
                            "time_limit": 30,
                            "type": "listing"
                        }
                    ]
                }
            ]
        }

    def get_next_document(self) -> Optional[Dict[str, Any]]:
        """
        Get next document with questions
        
        Returns:
            Dictionary with document data and questions or None if all documents used
        """
        # Try LLM generation first
        if self.use_llm and self.llm_provider:
            document = self._generate_dynamic_document()
            if document:
                return document
        
        # Fall back to static documents
        return self._get_fallback_document()

    def _get_fallback_document(self) -> Optional[Dict[str, Any]]:
        """Get a random fallback document from static pool"""
        try:
            fallback_set = self.fallback_documents.get(self.level, self.fallback_documents["beginner"])
            
            # Find unused documents
            available = [d for d in fallback_set if d["id"] not in self.documents_used]
            
            if not available:
                # Reset if all used
                self.documents_used.clear()
                available = fallback_set
            
            if not available:
                return None
            
            document_data = random.choice(available)
            self.documents_used.add(document_data["id"])
            
            return {
                "id": document_data["id"],
                "part": 4,
                "level": self.level,
                "task_type": "document_based_questions",
                "document_type": document_data["document_type"],
                "document": document_data["document"],
                "questions": document_data["questions"],
                "preparation_time": 45,  # 45 seconds to read document
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠ Failed to get fallback document: {e}")
            return None

    def _generate_dynamic_document(self) -> Optional[Dict[str, Any]]:
        """Generate a document and questions using LLM (Gemini)"""
        if not self.use_llm or not self.llm_provider:
            return None
        
        try:
            raw_response = self._generate_with_gemini()
            
            if not raw_response:
                return None
            
            parsed = self._parse_llm_response(raw_response)
            if not parsed:
                return None
            
            document = {
                "id": str(uuid.uuid4())[:8],
                "task_type": "document_based_questions",
                "part": 4,
                "level": self.level,
                "document_type": parsed.get("document_type", "Business Document"),
                "document": parsed.get("document", ""),
                "questions": parsed.get("questions", []),
                "preparation_time": 45,
                "created_at": datetime.now().isoformat()
            }
            
            return document
        except Exception as e:
            print(f"⚠ Failed to generate dynamic document: {e}")
            return None

    def _generate_with_gemini(self) -> Optional[str]:
        """Generate document and questions using Gemini API"""
        if not self.llm_client:
            return None
        
        prompt = f"""Generate a TOEIC Speaking Part 4 document and questions set.

The document should be for {self.level} level and be one of:
- Conference/Meeting Schedule
- Employee Handbook Policy
- Project Timeline
- Training Program Schedule
- Budget Report
- Shipping/Logistics Schedule
- Itinerary or Travel Document

Create 3 questions:
1. Question 8 (15s response): Basic factual detail (Who, What, Where, When)
2. Question 9 (15s response): Specific detail or confirmation
3. Question 10 (30s response): List multiple items from the document

Format your response as:
DOCUMENT_TYPE: [type]
DOCUMENT:
[multiline document content]
END_DOCUMENT

QUESTION_8: [question text]
QUESTION_9: [question text]
QUESTION_10: [question text]"""

        try:
            model = self.preferred_model
            response = self.llm_client.models.generate_content(
                model=model,
                contents=prompt,
                config={"max_output_tokens": 1500}
            )
            
            if response and response.text:
                return response.text
            return None
        except Exception as e:
            print(f"⚠ Gemini generation failed: {e}")
            return None

    def _parse_llm_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response into structured data"""
        try:
            lines = raw_response.strip().split('\n')
            result = {}
            document_lines = []
            in_document = False
            questions = {}
            
            for line in lines:
                if line.startswith('DOCUMENT_TYPE:'):
                    result['document_type'] = line.replace('DOCUMENT_TYPE:', '').strip()
                elif line.startswith('DOCUMENT:'):
                    in_document = True
                elif line.startswith('END_DOCUMENT'):
                    in_document = False
                elif line.startswith('QUESTION_8:'):
                    questions[8] = line.replace('QUESTION_8:', '').strip()
                elif line.startswith('QUESTION_9:'):
                    questions[9] = line.replace('QUESTION_9:', '').strip()
                elif line.startswith('QUESTION_10:'):
                    questions[10] = line.replace('QUESTION_10:', '').strip()
                elif in_document:
                    document_lines.append(line)
            
            if document_lines:
                result['document'] = '\n'.join(document_lines)
            
            if questions:
                result['questions'] = [
                    {"number": 8, "text": questions.get(8, ""), "time_limit": 15, "type": "factual"},
                    {"number": 9, "text": questions.get(9, ""), "time_limit": 15, "type": "specific"},
                    {"number": 10, "text": questions.get(10, ""), "time_limit": 30, "type": "listing"}
                ]
            
            if 'document' in result and 'questions' in result:
                return result
            return None
        except Exception as e:
            print(f"⚠ Failed to parse LLM response: {e}")
            return None

    def reset_documents(self) -> None:
        """Reset used documents for re-practice"""
        self.documents_used.clear()
