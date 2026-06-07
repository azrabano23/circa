"""Gmail integration service"""
from typing import List, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self, access_token: str, refresh_token: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    async def list_messages(
        self,
        query: str = '',
        max_results: int = 50,
        label_ids: Optional[List[str]] = None
    ) -> List[dict]:
        """List messages matching query"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                labelIds=label_ids or ['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    async def get_message(self, message_id: str) -> Optional[dict]:
        """Get a specific message by ID"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return self._parse_message(message)
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def _parse_message(self, message: dict) -> dict:
        """Parse Gmail message into a more usable format"""
        headers = message['payload']['headers']
        
        subject = next(
            (h['value'] for h in headers if h['name'].lower() == 'subject'),
            'No Subject'
        )
        sender = next(
            (h['value'] for h in headers if h['name'].lower() == 'from'),
            'Unknown'
        )
        date = next(
            (h['value'] for h in headers if h['name'].lower() == 'date'),
            ''
        )
        
        # Get email body
        body = self._get_message_body(message['payload'])
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'from': sender,
            'date': date,
            'snippet': message.get('snippet', ''),
            'body': body,
            'labels': message.get('labelIds', [])
        }
    
    def _get_message_body(self, payload: dict) -> str:
        """Extract message body from payload"""
        if 'parts' in payload:
            parts = payload['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                elif 'parts' in part:
                    return self._get_message_body(part)
        elif 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return ''
    
    async def search_deadlines(
        self,
        keywords: List[str] = None,
        after_date: Optional[datetime] = None
    ) -> List[dict]:
        """Search for emails containing potential deadlines"""
        if keywords is None:
            keywords = ['due', 'deadline', 'assignment', 'exam', 'quiz', 'submit']
        
        query_parts = [f'({" OR ".join(keywords)})']
        
        if after_date:
            date_str = after_date.strftime('%Y/%m/%d')
            query_parts.append(f'after:{date_str}')
        
        query = ' '.join(query_parts)
        
        message_ids = await self.list_messages(query=query, max_results=20)
        
        messages = []
        for msg in message_ids:
            full_message = await self.get_message(msg['id'])
            if full_message:
                messages.append(full_message)
        
        return messages

