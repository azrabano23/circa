"""Canvas LMS integration service"""
from typing import List, Optional
from datetime import datetime
import httpx


class CanvasLMSService:
    """Service for interacting with Canvas LMS API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def get_courses(self) -> List[dict]:
        """Get all active courses for the user"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.api_url}/courses',
                headers=self.headers,
                params={
                    'enrollment_state': 'active',
                    'per_page': 100
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return []
    
    async def get_assignments(self, course_id: str) -> List[dict]:
        """Get all assignments for a course"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.api_url}/courses/{course_id}/assignments',
                headers=self.headers,
                params={'per_page': 100}
            )
            
            if response.status_code == 200:
                return response.json()
            return []
    
    async def get_all_assignments(self) -> List[dict]:
        """Get all assignments from all active courses"""
        courses = await self.get_courses()
        all_assignments = []
        
        for course in courses:
            course_id = course['id']
            course_name = course.get('name', 'Unknown Course')
            
            assignments = await self.get_assignments(course_id)
            
            for assignment in assignments:
                assignment['course_name'] = course_name
                assignment['course_id'] = course_id
                all_assignments.append(assignment)
        
        return all_assignments
    
    async def get_upcoming_assignments(
        self,
        days_ahead: int = 30
    ) -> List[dict]:
        """Get upcoming assignments within the next N days"""
        all_assignments = await self.get_all_assignments()
        now = datetime.utcnow()
        
        upcoming = []
        for assignment in all_assignments:
            due_at = assignment.get('due_at')
            if due_at:
                due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                days_until_due = (due_date - now).days
                
                if 0 <= days_until_due <= days_ahead:
                    assignment['days_until_due'] = days_until_due
                    upcoming.append(assignment)
        
        # Sort by due date
        upcoming.sort(key=lambda x: x.get('due_at', ''))
        
        return upcoming
    
    async def get_announcements(self, course_id: str) -> List[dict]:
        """Get announcements for a course"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.api_url}/courses/{course_id}/discussion_topics',
                headers=self.headers,
                params={
                    'only_announcements': True,
                    'per_page': 50
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return []
    
    async def get_all_announcements(self) -> List[dict]:
        """Get all announcements from all active courses"""
        courses = await self.get_courses()
        all_announcements = []
        
        for course in courses:
            course_id = course['id']
            course_name = course.get('name', 'Unknown Course')
            
            announcements = await self.get_announcements(course_id)
            
            for announcement in announcements:
                announcement['course_name'] = course_name
                announcement['course_id'] = course_id
                all_announcements.append(announcement)
        
        return all_announcements
    
    async def get_calendar_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get calendar events"""
        params = {
            'type': 'assignment',
            'per_page': 100
        }
        
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.api_url}/calendar_events',
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            return []

