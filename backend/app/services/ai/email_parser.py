"""AI service for parsing emails to extract deadlines and tasks"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from openai import AsyncOpenAI
from app.core.config import settings


class EmailParser:
    """Parse emails using AI to extract deadlines and tasks"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def parse_email(
        self,
        subject: str,
        body: str,
        sender: str = "",
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Parse an email to extract tasks and deadlines"""
        
        if not self.client:
            # Fallback to rule-based parsing if OpenAI not configured
            return self._rule_based_parse(subject, body, sender, date)
        
        try:
            prompt = f"""
Analyze this email and extract any deadlines, assignments, or tasks.
Return a JSON object with the following structure:
{{
    "tasks": [
        {{
            "title": "task title",
            "due_date": "ISO date string or null",
            "priority": "low/medium/high/urgent",
            "estimated_duration": minutes (integer or null),
            "description": "brief description",
            "type": "assignment/exam/quiz/meeting/other"
        }}
    ],
    "confidence": 0.0 to 1.0
}}

Email details:
From: {sender}
Subject: {subject}
Body:
{body[:2000]}  # Limit body length
"""
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that extracts tasks and deadlines from emails. Be conservative - only extract clear, explicit tasks and deadlines."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in AI email parsing: {e}")
            return self._rule_based_parse(subject, body, sender, date)
    
    def _rule_based_parse(
        self,
        subject: str,
        body: str,
        sender: str,
        date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Fallback rule-based parsing when AI is not available"""
        
        tasks = []
        text = f"{subject} {body}".lower()
        
        # Common keywords for tasks
        task_keywords = {
            'assignment': {'keywords': ['assignment', 'homework', 'submit'], 'type': 'assignment'},
            'exam': {'keywords': ['exam', 'test', 'quiz', 'midterm', 'final'], 'type': 'exam'},
            'meeting': {'keywords': ['meeting', 'appointment', 'office hours'], 'type': 'meeting'},
        }
        
        # Find task type
        task_type = 'other'
        for ttype, data in task_keywords.items():
            if any(keyword in text for keyword in data['keywords']):
                task_type = data['type']
                break
        
        # Look for due dates
        due_date = self._extract_date(text, date)
        
        # Determine priority based on keywords
        priority = 'medium'
        if any(word in text for word in ['urgent', 'asap', 'important']):
            priority = 'high'
        elif any(word in text for word in ['exam', 'test', 'final']):
            priority = 'urgent'
        
        # If we found indicators of a task, add it
        if any(word in text for word in ['due', 'deadline', 'submit', 'assignment', 'exam', 'quiz']):
            tasks.append({
                'title': subject[:100],
                'due_date': due_date.isoformat() if due_date else None,
                'priority': priority,
                'estimated_duration': 120,  # Default 2 hours
                'description': body[:200],
                'type': task_type
            })
        
        return {
            'tasks': tasks,
            'confidence': 0.6 if tasks else 0.3
        }
    
    def _extract_date(self, text: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
        """Extract dates from text using regex patterns"""
        if reference_date is None:
            reference_date = datetime.now()
        
        # Pattern: Month Day, Year or Month Day
        date_patterns = [
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:,?\s+(\d{4}))?',
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})',
            r'due\s+(?:on\s+)?(\w+day)',  # "due Monday"
        ]
        
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    
                    # Month name pattern
                    if groups[0].lower() in months:
                        month = months[groups[0].lower()]
                        day = int(groups[1])
                        year = int(groups[2]) if groups[2] else reference_date.year
                        return datetime(year, month, day)
                    
                    # Weekday pattern
                    elif groups[0].lower().replace('day', '') in ['mon', 'tues', 'wednes', 'thurs', 'fri', 'satur', 'sun']:
                        # Find next occurrence of this weekday
                        target_day = weekdays.get(groups[0].lower(), None)
                        if target_day is not None:
                            days_ahead = target_day - reference_date.weekday()
                            if days_ahead <= 0:
                                days_ahead += 7
                            return reference_date + timedelta(days=days_ahead)
                    
                    # Numeric date pattern
                    else:
                        month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                        if year < 100:
                            year += 2000
                        return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def batch_parse_emails(
        self,
        emails: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse multiple emails in batch"""
        results = []
        
        for email in emails:
            result = await self.parse_email(
                subject=email.get('subject', ''),
                body=email.get('body', ''),
                sender=email.get('from', ''),
                date=email.get('date')
            )
            
            result['email_id'] = email.get('id')
            results.append(result)
        
        return results

