from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.models.event import Event
from app.models.task import Task, TaskStatus
from app.models.health_data import HealthData
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/daily")
async def get_daily_dashboard(
    date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily dashboard with events, tasks, and insights"""
    target_date = date or datetime.utcnow()
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Get events for the day
    events_result = await db.execute(
        select(Event).filter(
            and_(
                Event.user_id == current_user.id,
                Event.start_time >= start_of_day,
                Event.start_time < end_of_day
            )
        ).order_by(Event.start_time)
    )
    events = events_result.scalars().all()
    
    # Get tasks due today or scheduled for today
    tasks_result = await db.execute(
        select(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status != TaskStatus.COMPLETED,
                Task.due_date >= start_of_day,
                Task.due_date < end_of_day
            )
        ).order_by(Task.priority.desc(), Task.due_date)
    )
    tasks = tasks_result.scalars().all()
    
    # Get health data for the day
    health_result = await db.execute(
        select(HealthData).filter(
            and_(
                HealthData.user_id == current_user.id,
                HealthData.date == target_date.date()
            )
        )
    )
    health_data = health_result.scalar_one_or_none()
    
    # Calculate some metrics
    total_scheduled_time = sum(
        [(e.end_time - e.start_time).total_seconds() / 3600 for e in events],
        0
    )
    
    return {
        "date": target_date.date(),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time,
                "end_time": e.end_time,
                "type": e.event_type,
                "location": e.location
            } for e in events
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "priority": t.priority,
                "estimated_duration": t.estimated_duration,
                "optimal_time": t.optimal_time_of_day
            } for t in tasks
        ],
        "health": {
            "steps": health_data.steps if health_data else None,
            "sleep_hours": health_data.sleep_hours if health_data else None,
            "workout_completed": health_data.workout_duration > 0 if health_data else False
        } if health_data else None,
        "metrics": {
            "total_events": len(events),
            "total_tasks": len(tasks),
            "scheduled_hours": round(total_scheduled_time, 1),
            "free_hours": round(24 - total_scheduled_time, 1)
        }
    }


@router.get("/weekly")
async def get_weekly_dashboard(
    start_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly dashboard with review and analytics"""
    target_date = start_date or datetime.utcnow()
    week_start = target_date - timedelta(days=target_date.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    # Get all events for the week
    events_result = await db.execute(
        select(Event).filter(
            and_(
                Event.user_id == current_user.id,
                Event.start_time >= week_start,
                Event.start_time < week_end
            )
        ).order_by(Event.start_time)
    )
    events = events_result.scalars().all()
    
    # Get tasks completed this week
    completed_tasks_result = await db.execute(
        select(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status == TaskStatus.COMPLETED,
                Task.completed_at >= week_start,
                Task.completed_at < week_end
            )
        )
    )
    completed_tasks = completed_tasks_result.scalars().all()
    
    # Get pending tasks
    pending_tasks_result = await db.execute(
        select(Task).filter(
            and_(
                Task.user_id == current_user.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
            )
        )
    )
    pending_tasks = pending_tasks_result.scalars().all()
    
    # Calculate weekly metrics
    total_study_time = sum(
        [(e.end_time - e.start_time).total_seconds() / 3600 
         for e in events if e.event_type == "study"],
        0
    )
    
    total_gym_time = sum(
        [(e.end_time - e.start_time).total_seconds() / 3600 
         for e in events if e.event_type == "gym"],
        0
    )
    
    return {
        "week_start": week_start.date(),
        "week_end": week_end.date(),
        "summary": {
            "total_events": len(events),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "study_hours": round(total_study_time, 1),
            "gym_hours": round(total_gym_time, 1)
        },
        "daily_breakdown": [
            {
                "date": (week_start + timedelta(days=i)).date(),
                "events_count": len([
                    e for e in events 
                    if e.start_time.date() == (week_start + timedelta(days=i)).date()
                ])
            } for i in range(7)
        ],
        "upcoming_deadlines": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "priority": t.priority
            } for t in pending_tasks 
            if t.due_date and t.due_date < week_end + timedelta(days=7)
        ]
    }


@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered insights and recommendations"""
    # TODO: Implement AI-powered insights
    return {
        "productivity_score": 75,
        "insights": [
            "You're most productive in the morning between 9-11 AM",
            "Consider scheduling important tasks during your peak hours",
            "You've completed 80% of your tasks this week - great job!"
        ],
        "recommendations": [
            "Schedule your gym session earlier to boost morning energy",
            "Block 2-hour focus sessions for deep work on complex assignments",
            "Take a 15-minute break every 90 minutes for optimal focus"
        ]
    }

