# Circa Architecture

## Overview

Circa is a full-stack smart calendar application built with a modern microservices-inspired architecture. It combines real-time data synchronization, AI-powered scheduling optimization, and multiple third-party integrations.

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary relational database
- **Redis** - Caching and message broker
- **Celery** - Distributed task queue for background jobs
- **OpenAI API** - Natural language processing and AI features
- **Alembic** - Database migrations

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Query** - Data fetching and state management
- **Zustand** - Lightweight state management
- **FullCalendar** - Calendar visualization
- **Recharts** - Analytics and charts

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (production)

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Dashboard │  │ Calendar │  │  Tasks   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Integrate │  │ Settings │  │  Auth    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────┐
│                 Backend (FastAPI)                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │              API Layer (Routes)                     │ │
│  │  /auth  /events  /tasks  /dashboard  /ai  /users  │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  ┌──────────────────┴─────────────────────────────────┐ │
│  │             Service Layer                           │ │
│  │  ┌──────────────┐  ┌──────────────┐               │ │
│  │  │ Integrations │  │  AI Services │               │ │
│  │  │  - Google    │  │  - Parser    │               │ │
│  │  │  - Canvas    │  │  - Scheduler │               │ │
│  │  │  - Notion    │  │  - Optimizer │               │ │
│  │  │  - Gmail     │  │              │               │ │
│  │  │  - Health    │  │              │               │ │
│  │  └──────────────┘  └──────────────┘               │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  ┌──────────────────┴─────────────────────────────────┐ │
│  │             Data Layer (ORM)                        │ │
│  │  User | Event | Task | Integration | Preferences   │ │
│  └──────────────────┬─────────────────────────────────┘ │
└────────────────────┬┴──────────────────────────────────┘
                     │
    ┌────────────────┼────────────────────┐
    │                │                    │
┌───┴────┐    ┌──────┴──────┐    ┌──────┴──────┐
│  DB    │    │    Redis    │    │   Celery    │
│Postgres│    │   Cache     │    │   Worker    │
└────────┘    └─────────────┘    └─────────────┘
    │                │                    │
    │         ┌──────┴──────────────┐    │
    │         │                     │    │
┌───┴────┐ ┌──┴──────┐ ┌──────────┴┴────┴─┐
│External│ │Background│ │    Third-Party   │
│ APIs   │ │  Jobs    │ │    Services      │
│        │ │  - Sync  │ │  - Google APIs   │
│        │ │  - Parse │ │  - Canvas API    │
│        │ │  - Notify│ │  - Notion API    │
└────────┘ └──────────┘ └──────────────────┘
```

## Database Schema

### Core Tables

#### users
- `id` - Primary key
- `email` - Unique email
- `hashed_password` - Bcrypt hashed password
- `full_name` - User's full name
- `google_id` - OAuth Google ID
- `is_active` - Account status
- `created_at`, `updated_at` - Timestamps

#### events
- `id` - Primary key
- `user_id` - Foreign key to users
- `title`, `description`, `location` - Event details
- `start_time`, `end_time` - Event timing
- `event_type` - Type (class, exam, meeting, etc.)
- `source` - Where event came from (google, manual, etc.)
- `external_id` - ID in external system
- `is_flexible` - Can be rescheduled
- `priority` - 1-5 priority level

#### tasks
- `id` - Primary key
- `user_id` - Foreign key to users
- `title`, `description` - Task details
- `due_date` - When task is due
- `scheduled_start`, `scheduled_end` - Scheduled time
- `estimated_duration` - Expected minutes
- `status` - todo, in_progress, completed, cancelled
- `priority` - low, medium, high, urgent
- `ai_extracted` - Was task extracted by AI
- `difficulty_score` - AI-estimated difficulty (0-1)
- `optimal_time_of_day` - When to schedule

#### integrations
- `id` - Primary key
- `user_id` - Foreign key to users
- `provider` - google, canvas, notion, etc.
- `access_token`, `refresh_token` - OAuth tokens
- `config` - JSON config
- `last_sync_at` - Last sync timestamp
- `sync_enabled` - Auto-sync enabled

#### user_preferences
- `id` - Primary key
- `user_id` - Foreign key to users (unique)
- `wake_time`, `sleep_time` - Sleep schedule
- `peak_focus_time` - morning, afternoon, evening
- `study_session_duration` - Minutes
- `gym_frequency` - Times per week
- `auto_reschedule` - Enable auto-rescheduling
- Plus many more preference fields

#### health_data
- `id` - Primary key
- `user_id` - Foreign key to users
- `date` - Date of data
- `steps`, `active_minutes`, `calories_burned` - Activity
- `sleep_hours`, `sleep_quality` - Sleep metrics
- `resting_heart_rate` - Heart rate
- `stress_level`, `recovery_score` - Wellness

#### quiz_responses
- `id` - Primary key
- `user_id` - Foreign key to users
- `quiz_type` - onboarding, periodic, adaptive
- `questions`, `answers` - JSON arrays
- `insights` - AI-generated insights
- `completed_at` - Completion timestamp

## Data Flow

### 1. User Registration & Onboarding

```
User → Frontend → POST /auth/register → Backend
                                         ↓
                                    Create User
                                         ↓
                                    PostgreSQL
                                         ↓
Frontend ← Return Success ← Backend
     ↓
Redirect to Onboarding
     ↓
GET /ai/quiz/onboarding → Backend → Return Questions
     ↓
User Answers
     ↓
POST /ai/quiz/submit → Backend → OpenAI API (analyze)
                                      ↓
                                 Save Preferences
                                      ↓
                                  PostgreSQL
```

### 2. Integration Sync

```
User → Connect Integration → Frontend → POST /integrations/canvas/connect
                                                  ↓
                                         Store Credentials
                                                  ↓
                                             PostgreSQL
                                                  ↓
                                         Trigger Background Job
                                                  ↓
                                            Celery Worker
                                                  ↓
                                           Canvas LMS API
                                                  ↓
                                         Fetch Assignments
                                                  ↓
                                      Create Tasks in Database
                                                  ↓
                                             PostgreSQL
                                                  ↓
Frontend (auto-refresh) ← Return Success ← Backend
```

### 3. AI Email Parsing

```
Gmail Integration → Fetch New Emails → Celery Worker (Background)
                                              ↓
                                       Parse with OpenAI
                                              ↓
                                   Extract Deadlines/Tasks
                                              ↓
                                  Save to Database (with ai_extracted=true)
                                              ↓
                                         PostgreSQL
                                              ↓
User opens Dashboard → Frontend → GET /dashboard/daily
                                       ↓
                              Return Events + Tasks
                                       ↓
                              Display AI-extracted items
```

### 4. Schedule Optimization

```
User → Request Optimization → POST /ai/optimize-schedule
                                          ↓
                                  Get User Preferences
                                          ↓
                                     PostgreSQL
                                          ↓
                               Get Events, Tasks, Health Data
                                          ↓
                                     PostgreSQL
                                          ↓
                                AI Scheduler Algorithm
                                   (considers:
                                    - Circadian rhythm
                                    - Task difficulty
                                    - Deadlines
                                    - Health data
                                    - Preferences)
                                          ↓
                               Generate Optimal Schedule
                                          ↓
                             Update scheduled_start/end times
                                          ↓
                                     PostgreSQL
                                          ↓
Frontend ← Return Optimized Schedule ← Backend
```

## Key Components

### Backend Services

#### Integration Services (`app/services/integrations/`)
- **google_calendar.py** - Sync events from Google Calendar
- **gmail.py** - Fetch and parse emails
- **canvas_lms.py** - Import assignments and deadlines
- **notion.py** - Sync tasks from Notion databases
- **health.py** - Aggregate health data from multiple sources

#### AI Services (`app/services/ai/`)
- **email_parser.py** - Extract tasks from email content using GPT-4
- **scheduler.py** - Optimize schedule based on user preferences and constraints

### Frontend Components

#### Pages (`frontend/src/pages/`)
- **Dashboard.tsx** - Main dashboard with daily overview
- **Calendar.tsx** - Interactive calendar view
- **Tasks.tsx** - Task management
- **Integrations.tsx** - Connect external services
- **Settings.tsx** - User preferences
- **Login.tsx** / **Register.tsx** - Authentication
- **Onboarding.tsx** - Initial quiz

#### Services (`frontend/src/services/`)
- **api.ts** - API client with interceptors
- Handles authentication tokens
- Error handling and retries

#### State Management (`frontend/src/store/`)
- **authStore.ts** - User authentication state (Zustand + localStorage)

## Security

### Authentication
- JWT tokens with configurable expiration
- Bcrypt password hashing
- OAuth2 for Google integration

### API Security
- CORS configuration
- Rate limiting (implemented at proxy level)
- Input validation with Pydantic
- SQL injection prevention via ORM

### Data Protection
- Encrypted token storage
- HTTPS in production
- Environment variables for secrets
- No sensitive data in logs

## Performance Optimizations

### Backend
- Async/await for I/O operations
- Connection pooling for database
- Redis caching for frequent queries
- Background jobs for expensive operations

### Frontend
- React Query for data caching
- Code splitting with Vite
- Lazy loading of routes
- Optimistic UI updates

### Database
- Indexes on frequently queried fields
- Pagination for large datasets
- Query optimization with `select_related`

## Scalability Considerations

### Current Architecture
- Monolithic backend (suitable for MVP)
- Single database instance
- Single Redis instance

### Future Improvements
- Microservices for integrations
- Database sharding by user_id
- Redis cluster for caching
- CDN for static assets
- Message queue for async communication
- Kubernetes for orchestration

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Docker containers behind Nginx reverse proxy
- PostgreSQL with regular backups
- Redis persistence enabled
- SSL/TLS certificates
- Monitoring with Prometheus/Grafana
- Logging with ELK stack

## Monitoring & Logging

### Metrics to Track
- API response times
- Database query performance
- Background job success/failure rates
- Integration sync status
- User activity patterns

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Separate logs for:
  - Application logs
  - Access logs
  - Error logs
  - Background job logs

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- Mock external APIs
- Database transactions for test isolation

### Frontend Tests
- Component tests with React Testing Library
- E2E tests with Playwright
- API mocking with MSW

## Future Enhancements

1. **Real-time Updates**
   - WebSocket connections
   - Live schedule changes

2. **Mobile App**
   - React Native
   - Push notifications

3. **Advanced AI**
   - Custom ML models for user patterns
   - Predictive task duration
   - Smart conflict resolution

4. **Collaboration**
   - Shared calendars
   - Team scheduling
   - Meeting polls

5. **Analytics**
   - Productivity dashboards
   - Time tracking
   - Goal achievement metrics

---

This architecture provides a solid foundation for a scalable, maintainable calendar optimization system.

