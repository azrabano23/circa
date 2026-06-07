"""Google OAuth implementation for Calendar and Gmail"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.integration import Integration
from app.models.event import Event, EventSource, EventType
from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings

router = APIRouter()

# Google OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
]


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {
        "authorization_url": authorization_url,
        "state": state
    }


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info
    # For now, return success - in production, store tokens and associate with user
    return {
        "message": "Google OAuth successful",
        "redirect": "http://localhost:3000/integrations?success=google"
    }


@router.post("/google/sync-calendar")
async def sync_google_calendar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync events from Google Calendar"""
    # Get user's Google integration
    result = await db.execute(
        select(Integration).filter(
            and_(
                Integration.user_id == current_user.id,
                Integration.provider == "google"
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Google Calendar not connected")
    
    # Build credentials
    creds = Credentials(
        token=integration.access_token,
        refresh_token=integration.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET
    )
    
    # Fetch calendar events
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    imported_count = 0
    
    for gcal_event in events:
        start = gcal_event['start'].get('dateTime', gcal_event['start'].get('date'))
        end = gcal_event['end'].get('dateTime', gcal_event['end'].get('date'))
        
        # Check if event already exists
        result = await db.execute(
            select(Event).filter(
                and_(
                    Event.user_id == current_user.id,
                    Event.external_id == gcal_event['id']
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            event = Event(
                user_id=current_user.id,
                title=gcal_event.get('summary', 'No Title'),
                description=gcal_event.get('description'),
                location=gcal_event.get('location'),
                start_time=datetime.fromisoformat(start.replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(end.replace('Z', '+00:00')),
                source=EventSource.GOOGLE_CALENDAR,
                external_id=gcal_event['id'],
                event_type=EventType.OTHER
            )
            db.add(event)
            imported_count += 1
    
    await db.commit()
    integration.last_sync_at = datetime.utcnow()
    await db.commit()
    
    return {
        "message": f"Successfully synced {imported_count} events from Google Calendar",
        "imported_count": imported_count
    }

