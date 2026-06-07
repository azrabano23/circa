from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class EmailParseRequest(BaseModel):
    email_content: str
    subject: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    question_type: str  # multiple_choice, scale, text


class QuizSubmission(BaseModel):
    quiz_type: str
    answers: List[dict]


@router.post("/parse-email")
async def parse_email_for_deadlines(
    request: EmailParseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Parse email content to extract deadlines and tasks using AI"""
    # TODO: Implement OpenAI integration for email parsing
    return {
        "extracted_tasks": [
            {
                "title": "Assignment 1 - Data Structures",
                "due_date": "2024-11-15T23:59:00Z",
                "priority": "high",
                "estimated_duration": 120,
                "source": "email"
            }
        ],
        "confidence": 0.92
    }


@router.post("/optimize-schedule")
async def optimize_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Use AI to optimize the user's schedule based on preferences and patterns"""
    # TODO: Implement schedule optimization algorithm
    return {
        "message": "Schedule optimization in progress",
        "optimized_tasks": [],
        "recommendations": [
            "Move studying to morning hours for better focus",
            "Schedule gym before dinner for improved sleep"
        ]
    }


@router.get("/quiz/onboarding")
async def get_onboarding_quiz(
    current_user: User = Depends(get_current_user)
):
    """
    Get research-based onboarding quiz to determine learning style and cognitive patterns.
    
    Based on research from:
    - Chronotype theory (Roenneberg et al., 2003)
    - Cognitive load theory (Sweller, 1988)
    - Learning styles (VARK model - Fleming & Mills, 1992)
    - Self-Determination Theory (Deci & Ryan, 1985)
    """
    questions = [
        {
            "id": "chronotype",
            "question": "When do you naturally feel most alert and productive? (Chronotype Assessment)",
            "options": [
                "Early morning (6-9 AM) - I wake up easily and feel energized",
                "Late morning (9 AM-12 PM) - I hit my stride mid-morning", 
                "Early afternoon (12-3 PM) - I'm sharpest after lunch",
                "Late afternoon/evening (3-7 PM) - I come alive in the afternoon",
                "Night (7 PM-12 AM) - I'm a night owl, most creative after dark"
            ],
            "type": "multiple_choice",
            "research": "Chronotype determines optimal cognitive performance windows"
        },
        {
            "id": "focus_duration",
            "question": "How long can you maintain deep focus on challenging material? (Attention Span)",
            "options": [
                "15-25 minutes (then I need a break)",
                "25-45 minutes (Pomodoro-style works well)",
                "45-90 minutes (I can do extended sessions)",
                "90-120 minutes (I prefer long deep work blocks)",
                "It varies greatly depending on the task"
            ],
            "type": "multiple_choice",
            "research": "Ultradian rhythms suggest 90-min cycles, but individual variation exists"
        },
        {
            "id": "learning_modality",
            "question": "How do you learn complex concepts best? (VARK Learning Style)",
            "options": [
                "Reading and writing - I need to take notes and read thoroughly",
                "Visual - diagrams, charts, videos, and visual aids help me",
                "Auditory - listening to lectures, discussions, explaining out loud",
                "Kinesthetic - hands-on practice, doing problems, building things",
                "Multimodal - I combine several approaches"
            ],
            "type": "multiple_choice",
            "research": "VARK model identifies dominant learning modalities"
        },
        {
            "id": "task_switching",
            "question": "How do you handle multiple subjects or projects?",
            "options": [
                "Interleaved - I switch between subjects in one session (better retention)",
                "Blocked - I prefer focusing on one subject per session",
                "Mixed - Short subjects interleaved, long projects blocked",
                "Context-dependent - Depends on deadlines and difficulty"
            ],
            "type": "multiple_choice",
            "research": "Interleaved practice improves long-term retention (Rohrer & Taylor, 2007)"
        },
        {
            "id": "procrastination_pattern",
            "question": "When do you typically start working on assignments? (Time Management)",
            "options": [
                "Immediately when assigned - I like getting ahead",
                "A week before due date - planned approach",
                "2-3 days before - moderate procrastination",
                "The night before - high-pressure works for me",
                "Hours before deadline - extreme time pressure motivates me"
            ],
            "type": "multiple_choice",
            "research": "Temporal motivation theory explains procrastination patterns"
        },
        {
            "id": "difficulty_preference",
            "question": "How do you prefer to tackle difficult tasks?",
            "options": [
                "Morning when I'm fresh - hardest tasks first",
                "After warming up with easier tasks",
                "Break them into smaller chunks throughout the day",
                "Save for when I have a long uninterrupted block",
                "Under deadline pressure when adrenaline kicks in"
            ],
            "type": "multiple_choice",
            "research": "Peak cognitive performance varies by chronotype and cognitive load"
        },
        {
            "id": "sleep_pattern",
            "question": "What's your typical sleep schedule? (Sleep Hygiene)",
            "options": [
                "Consistent early (sleep by 10 PM, wake by 6 AM)",
                "Consistent moderate (sleep by 11 PM, wake by 7 AM)",
                "Consistent late (sleep by 12-1 AM, wake by 8-9 AM)",
                "Very late (sleep after 1 AM, wake after 9 AM)",
                "Irregular - varies day to day"
            ],
            "type": "multiple_choice",
            "research": "Sleep consistency affects cognitive function (Walker, 2017)"
        },
        {
            "id": "break_activity",
            "question": "What recharges you during study breaks?",
            "options": [
                "Physical movement - walk, stretch, exercise",
                "Social interaction - talk to friends, check messages",
                "Complete rest - nap, meditate, close eyes",
                "Different mental activity - read news, watch videos",
                "Snacks and hydration"
            ],
            "type": "multiple_choice",
            "research": "Different break activities serve different recovery needs"
        },
        {
            "id": "environment_preference",
            "question": "Where do you study most effectively?",
            "options": [
                "Complete silence - library, quiet room",
                "Light background noise - coffee shop, soft music",
                "Active environment - with people around",
                "Varies by task - silence for hard, noise for easy",
                "Nature or outdoor settings when possible"
            ],
            "type": "multiple_choice",
            "research": "Environmental context affects encoding and retrieval"
        },
        {
            "id": "motivation_type",
            "question": "What motivates you most to complete tasks? (Motivation Style)",
            "options": [
                "Internal curiosity - I'm genuinely interested in learning",
                "Achievement - getting good grades, being the best",
                "External pressure - deadlines, consequences",
                "Social accountability - study groups, commitments to others",
                "Long-term goals - career, graduation, future plans"
            ],
            "type": "multiple_choice",
            "research": "Self-Determination Theory distinguishes intrinsic vs extrinsic motivation"
        },
        {
            "id": "stress_response",
            "question": "How do you perform under stress/pressure?",
            "options": [
                "I thrive - stress enhances my focus and performance",
                "Moderate stress helps - too much hurts performance",
                "I function but not optimally - prefer low pressure",
                "Stress significantly impairs my work quality",
                "Highly variable - depends on the type of stress"
            ],
            "type": "multiple_choice",
            "research": "Yerkes-Dodson law: moderate arousal optimal, but individual differences exist"
        },
        {
            "id": "energy_patterns",
            "question": "How would you describe your energy throughout the day?",
            "options": [
                "Steady - consistent energy all day",
                "Peak morning, crash afternoon (post-lunch dip)",
                "Slow start, building energy as day goes on",
                "Multiple peaks - morning and evening highs",
                "Chaotic - varies day to day"
            ],
            "type": "multiple_choice",
            "research": "Circadian rhythms and ultradian cycles affect performance"
        }
    ]
    
    return {
        "questions": questions,
        "research_note": "This quiz uses evidence-based frameworks from cognitive psychology, chronobiology, and learning science to optimize your schedule."
    }


@router.post("/quiz/submit")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit quiz responses and get personalized recommendations"""
    from app.models.quiz_response import QuizResponse
    
    # Save quiz response
    quiz_response = QuizResponse(
        user_id=current_user.id,
        quiz_type=submission.quiz_type,
        questions=[],  # Store questions
        answers=submission.answers,
        completed=True
    )
    
    db.add(quiz_response)
    await db.commit()
    
    # TODO: Analyze responses with AI to generate insights
    insights = {
        "chronotype": "morning person",
        "focus_duration": 60,
        "procrastination_level": "moderate",
        "recommendations": [
            "Schedule important tasks between 9-11 AM",
            "Use 50-minute focus sessions with 10-minute breaks",
            "Start tasks at least 3 days before deadline"
        ]
    }
    
    return {
        "message": "Quiz submitted successfully",
        "insights": insights
    }


@router.post("/analyze-productivity")
async def analyze_productivity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze user's productivity patterns using historical data"""
    # TODO: Implement productivity analysis
    return {
        "productivity_score": 78,
        "patterns": {
            "best_time_of_day": "morning",
            "average_focus_duration": 55,
            "task_completion_rate": 0.82
        },
        "suggestions": [
            "You complete 90% of tasks scheduled in the morning",
            "Consider reducing afternoon commitments",
            "Your gym sessions correlate with better sleep quality"
        ]
    }


@router.post("/schedule-from-prompt")
async def schedule_from_prompt(
    prompt: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered natural language scheduling.
    
    Example prompts:
    - "Study for CS midterm for 3 hours sometime this week"
    - "Schedule gym sessions 3 times next week in the morning"
    - "I need to finish my essay by Friday, schedule writing time"
    """
    from app.services.ai.email_parser import EmailParser
    from app.models.event import Event
    from app.models.task import Task, TaskPriority, TaskStatus
    from app.models.preference import UserPreference
    from datetime import timedelta
    from sqlalchemy import select, and_
    
    parser = EmailParser()
    
    # Use OpenAI to parse the natural language prompt
    if parser.client:
        try:
            system_prompt = """You are a scheduling assistant. Parse natural language scheduling requests into structured data.
Return JSON with:
{
  "task_title": "clear title",
  "duration_minutes": integer,
  "preferred_time": "morning/afternoon/evening/anytime",
  "deadline": "ISO date or null",
  "priority": "low/medium/high/urgent",
  "frequency": "once/daily/weekly/null",
  "context": "any additional context"
}"""
            
            response = await parser.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Schedule this: {prompt}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            parsed = json.loads(response.choices[0].message.content)
            
            # Get user preferences for optimal scheduling
            result = await db.execute(
                select(UserPreference).filter(UserPreference.user_id == current_user.id)
            )
            preferences = result.scalar_one_or_none()
            
            # Create task
            task = Task(
                user_id=current_user.id,
                title=parsed['task_title'],
                estimated_duration=parsed.get('duration_minutes', 60),
                priority=TaskPriority[parsed.get('priority', 'medium').upper()],
                status=TaskStatus.TODO,
                source="ai_prompt",
                ai_extracted=True,
                optimal_time_of_day=parsed.get('preferred_time', 'anytime')
            )
            
            if parsed.get('deadline'):
                task.due_date = datetime.fromisoformat(parsed['deadline'].replace('Z', '+00:00'))
            
            db.add(task)
            await db.commit()
            await db.refresh(task)
            
            # Now use AI to find optimal time slot
            from app.services.ai.scheduler import ScheduleOptimizer
            
            # Get existing events
            events_result = await db.execute(
                select(Event).filter(
                    and_(
                        Event.user_id == current_user.id,
                        Event.start_time >= datetime.utcnow(),
                        Event.start_time < datetime.utcnow() + timedelta(days=7)
                    )
                ).order_by(Event.start_time)
            )
            events = events_result.scalars().all()
            
            optimizer = ScheduleOptimizer(
                user_preferences=preferences.__dict__ if preferences else {},
                health_data={}
            )
            
            # Format events for optimizer
            events_dict = [{
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat()
            } for e in events]
            
            # Find optimal slot
            task_dict = {
                "id": task.id,
                "title": task.title,
                "estimated_duration": task.estimated_duration,
                "priority": task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
                "difficulty_score": task.difficulty_score or 0.5
            }
            
            schedule = optimizer.optimize_daily_schedule(
                [task_dict],
                events_dict,
                datetime.utcnow()
            )
            
            return {
                "message": "Task created and scheduled",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "duration": task.estimated_duration,
                    "priority": str(task.priority),
                    "optimal_time": task.optimal_time_of_day
                },
                "suggested_schedule": schedule.get('scheduled_tasks', []),
                "ai_recommendation": f"Based on your preferences, I recommend scheduling '{parsed['task_title']}' during {parsed.get('preferred_time', 'your optimal hours')}"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI scheduling failed: {str(e)}")
    else:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

