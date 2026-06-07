# Circa API Guide

Complete API reference for the Circa smart calendar application.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

Most endpoints require authentication using JWT tokens.

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header for all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Authentication

#### Register
```http
POST /auth/register

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer {token}
```

### Events

#### List Events
```http
GET /events/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

#### Create Event
```http
POST /events/
Authorization: Bearer {token}

{
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_time": "2024-11-15T10:00:00Z",
  "end_time": "2024-11-15T11:00:00Z",
  "event_type": "meeting",
  "location": "Conference Room A",
  "priority": 4
}
```

#### Update Event
```http
PUT /events/{event_id}
Authorization: Bearer {token}

{
  "title": "Updated Meeting Title",
  "start_time": "2024-11-15T11:00:00Z"
}
```

#### Delete Event
```http
DELETE /events/{event_id}
Authorization: Bearer {token}
```

### Tasks

#### List Tasks
```http
GET /tasks/?status=todo
Authorization: Bearer {token}
```

#### Create Task
```http
POST /tasks/
Authorization: Bearer {token}

{
  "title": "Complete Assignment 1",
  "description": "Data structures homework",
  "due_date": "2024-11-20T23:59:00Z",
  "priority": "high",
  "estimated_duration": 120
}
```

#### Update Task
```http
PUT /tasks/{task_id}
Authorization: Bearer {token}

{
  "status": "completed",
  "actual_duration": 90
}
```

### Dashboard

#### Daily Dashboard
```http
GET /dashboard/daily?date=2024-11-15
Authorization: Bearer {token}
```

**Response:**
```json
{
  "date": "2024-11-15",
  "events": [...],
  "tasks": [...],
  "health": {
    "steps": 8542,
    "sleep_hours": 7.5,
    "workout_completed": true
  },
  "metrics": {
    "total_events": 5,
    "total_tasks": 3,
    "scheduled_hours": 6.5,
    "free_hours": 17.5
  }
}
```

#### Weekly Dashboard
```http
GET /dashboard/weekly?start_date=2024-11-11
Authorization: Bearer {token}
```

#### Get Insights
```http
GET /dashboard/insights
Authorization: Bearer {token}
```

**Response:**
```json
{
  "productivity_score": 78,
  "insights": [
    "You're most productive in the morning between 9-11 AM",
    "Consider scheduling important tasks during your peak hours"
  ],
  "recommendations": [
    "Schedule your gym session earlier to boost morning energy",
    "Block 2-hour focus sessions for deep work on complex assignments"
  ]
}
```

### Integrations

#### List Integrations
```http
GET /integrations/
Authorization: Bearer {token}
```

#### Connect Canvas LMS
```http
POST /integrations/canvas/connect
Authorization: Bearer {token}

{
  "api_key": "your-canvas-api-key",
  "canvas_url": "https://canvas.instructure.com"
}
```

#### Connect Notion
```http
POST /integrations/notion/connect
Authorization: Bearer {token}

{
  "api_key": "secret_your-notion-key"
}
```

#### Sync Integration
```http
POST /integrations/{integration_id}/sync
Authorization: Bearer {token}
```

#### Disconnect Integration
```http
DELETE /integrations/{integration_id}
Authorization: Bearer {token}
```

### AI Services

#### Parse Email for Deadlines
```http
POST /ai/parse-email
Authorization: Bearer {token}

{
  "subject": "Assignment 1 Due Next Week",
  "email_content": "Your assignment for CS101 is due on November 20th at 11:59 PM..."
}
```

**Response:**
```json
{
  "extracted_tasks": [
    {
      "title": "CS101 Assignment 1",
      "due_date": "2024-11-20T23:59:00Z",
      "priority": "high",
      "estimated_duration": 120,
      "source": "email"
    }
  ],
  "confidence": 0.92
}
```

#### Optimize Schedule
```http
POST /ai/optimize-schedule
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Schedule optimization in progress",
  "optimized_tasks": [...],
  "recommendations": [
    "Move studying to morning hours for better focus",
    "Schedule gym before dinner for improved sleep"
  ]
}
```

#### Get Onboarding Quiz
```http
GET /ai/quiz/onboarding
Authorization: Bearer {token}
```

#### Submit Quiz
```http
POST /ai/quiz/submit
Authorization: Bearer {token}

{
  "quiz_type": "onboarding",
  "answers": [
    {"question_id": "q1", "answer": "Early morning (6-9 AM)"},
    {"question_id": "q2", "answer": "1-2 hours"}
  ]
}
```

#### Analyze Productivity
```http
POST /ai/analyze-productivity
Authorization: Bearer {token}
```

### User Preferences

#### Get Preferences
```http
GET /users/me/preferences
Authorization: Bearer {token}
```

#### Update Preferences
```http
PUT /users/me/preferences
Authorization: Bearer {token}

{
  "wake_time": "07:00",
  "sleep_time": "23:00",
  "peak_focus_time": "morning",
  "study_session_duration": 50,
  "break_duration": 10,
  "gym_frequency": 3,
  "workout_duration": 60,
  "auto_reschedule": true,
  "buffer_time": 15
}
```

## Event Types

- `class` - Class/lecture
- `exam` - Exam or test
- `assignment` - Assignment deadline
- `meeting` - Meeting
- `social` - Social event
- `gym` - Gym/workout
- `meal` - Meal time
- `study` - Study session
- `other` - Other type

## Task Status

- `todo` - Not started
- `in_progress` - Currently working on
- `completed` - Finished
- `cancelled` - Cancelled

## Task Priority

- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority
- `urgent` - Urgent/critical

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Standard endpoints: 100 requests per minute
- AI endpoints: 20 requests per minute
- Integration sync: 10 requests per hour

## Webhooks (Future Feature)

Circa will support webhooks for real-time updates:

```http
POST /webhooks/subscribe
Authorization: Bearer {token}

{
  "url": "https://your-app.com/webhook",
  "events": ["task.created", "event.updated", "schedule.optimized"]
}
```

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation with:
- Try-it-out functionality
- Request/response examples
- Schema definitions
- Authentication testing

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data={'username': 'user@example.com', 'password': 'password'}
)
token = response.json()['access_token']

# Get events
headers = {'Authorization': f'Bearer {token}'}
events = requests.get(
    'http://localhost:8000/api/v1/events/',
    headers=headers
).json()
```

### JavaScript

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await response.json();

// Get events
const events = await fetch('http://localhost:8000/api/v1/events/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
}).then(res => res.json());
```

### cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"

# Get events
curl -X GET "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

For more information, visit the interactive documentation at `/docs` or contact support.

