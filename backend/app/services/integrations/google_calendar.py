"""Google Calendar integration service"""
from typing import List, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    def __init__(self, access_token: str, refresh_token: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    async def list_calendars(self) -> List[dict]:
        """List all calendars"""
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    async def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[dict]:
        """Get events from a calendar"""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z' if time_min else None,
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[dict]:
        """Create a new event"""
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            return event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    async def update_event(
        self,
        event_id: str,
        updates: dict,
        calendar_id: str = 'primary'
    ) -> Optional[dict]:
        """Update an existing event"""
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            event.update(updates)
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return updated_event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """Delete an event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

