"""Manual import endpoint for Canvas assignments (workaround for no API access)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.task import Task, TaskPriority, TaskStatus
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class ManualAssignment(BaseModel):
    title: str
    course_name: str
    due_date: datetime
    points: Optional[float] = None
    description: Optional[str] = None


class BulkImportRequest(BaseModel):
    assignments: List[ManualAssignment]


@router.post("/canvas/manual")
async def manual_import_canvas(
    data: BulkImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually import Canvas assignments without API access.
    
    This is a workaround for when Canvas API key is not available.
    Users can copy/paste assignment info from Canvas.
    """
    
    imported_count = 0
    tasks_created = []
    
    for assignment in data.assignments:
        # Create task from assignment
        task = Task(
            user_id=current_user.id,
            title=f"{assignment.course_name}: {assignment.title}",
            description=assignment.description or f"Assignment worth {assignment.points} points" if assignment.points else None,
            due_date=assignment.due_date,
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            source="canvas_manual",
            estimated_duration=120,  # Default 2 hours
        )
        
        db.add(task)
        imported_count += 1
        tasks_created.append({
            "title": task.title,
            "due_date": task.due_date
        })
    
    await db.commit()
    
    return {
        "message": f"Successfully imported {imported_count} assignments",
        "imported_count": imported_count,
        "tasks": tasks_created
    }


@router.post("/canvas/paste")
async def paste_canvas_assignments(
    text: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Parse pasted text from Canvas and create tasks.
    
    This endpoint uses AI to parse copied text from Canvas pages
    and extract assignment information.
    """
    from app.services.ai.email_parser import EmailParser
    from app.models.task import Task, TaskPriority, TaskStatus
    from datetime import datetime
    
    parser = EmailParser()
    
    # Use AI to parse the pasted content
    result = await parser.parse_email(
        subject="Canvas Assignments",
        body=text,
        sender="Canvas"
    )
    
    imported_count = 0
    tasks_created = []
    
    for extracted_task in result.get('tasks', []):
        # Parse due date safely
        due_date = None
        if extracted_task.get('due_date'):
            try:
                due_date = datetime.fromisoformat(extracted_task['due_date'].replace('Z', '+00:00'))
            except:
                pass
        
        # Parse priority safely
        priority_str = extracted_task.get('priority', 'medium').upper()
        try:
            priority = TaskPriority[priority_str]
        except KeyError:
            priority = TaskPriority.MEDIUM
        
        task = Task(
            user_id=current_user.id,
            title=extracted_task['title'],
            description=extracted_task.get('description'),
            due_date=due_date,
            status=TaskStatus.TODO,
            priority=priority,
            source="canvas_paste",
            ai_extracted=True,
            estimated_duration=extracted_task.get('estimated_duration', 120),
        )
        
        db.add(task)
        imported_count += 1
        tasks_created.append({
            "title": task.title,
            "due_date": task.due_date
        })
    
    await db.commit()
    
    return {
        "message": f"Successfully imported {imported_count} assignments from pasted text",
        "imported_count": imported_count,
        "confidence": result.get('confidence', 0.0),
        "tasks": tasks_created
    }


@router.get("/canvas/help")
async def get_import_help():
    """Get instructions for manually importing Canvas assignments"""
    return {
        "title": "How to Import Canvas Assignments Manually",
        "methods": [
            {
                "name": "Method 1: Copy & Paste",
                "steps": [
                    "1. Go to your Canvas Assignments page",
                    "2. Copy the assignment list (Ctrl+A, Ctrl+C)",
                    "3. Paste into Circa's import box",
                    "4. Our AI will extract assignments automatically"
                ],
                "pros": "Quick and easy",
                "endpoint": "/manual-import/canvas/paste"
            },
            {
                "name": "Method 2: Manual Entry",
                "steps": [
                    "1. Click 'Add Assignment' in Circa",
                    "2. Fill in: Title, Course, Due Date",
                    "3. Repeat for each assignment"
                ],
                "pros": "Most accurate",
                "endpoint": "/manual-import/canvas/manual"
            },
            {
                "name": "Method 3: Use Calendar Export",
                "steps": [
                    "1. In Canvas, go to Calendar Feed",
                    "2. Copy the calendar URL",
                    "3. Add to Google Calendar",
                    "4. Circa will sync via Google Calendar"
                ],
                "pros": "Automatic updates",
                "note": "Requires Google Calendar integration"
            }
        ],
        "tips": [
            "Copy multiple assignments at once for bulk import",
            "Include course names in your paste for better organization",
            "The AI can understand dates in many formats",
            "Review imported tasks and adjust priorities as needed"
        ]
    }

