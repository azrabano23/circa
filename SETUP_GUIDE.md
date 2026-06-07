# Circa - Setup Guide

This guide will help you set up and run the Circa smart calendar application on your local machine.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download Node.js](https://nodejs.org/)
- **PostgreSQL 15+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+** - [Download Redis](https://redis.io/download/)
- **Docker & Docker Compose** (recommended) - [Download Docker](https://www.docker.com/products/docker-desktop/)

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
cd circa

# 2. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Add your API keys to backend/.env (see API Keys section below)

# 4. Start all services
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The application should now be running.

## Manual Setup

If you prefer to run the services individually:

### 1. Database Setup

Create a PostgreSQL database:

```bash
# Using psql
createdb circa_db

# Or using SQL
psql -U postgres
CREATE DATABASE circa_db;
CREATE USER circa_user WITH PASSWORD 'circa_password';
GRANT ALL PRIVILEGES ON DATABASE circa_db TO circa_user;
\q
```

Start Redis:

```bash
redis-server
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for NLP
python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys (see below)

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload

# In a separate terminal, start the Celery worker
celery -A app.celery_worker worker --loglevel=info
```

The backend API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000

## API Keys Configuration

To enable all features, you'll need to obtain API keys from the following services:

### Required API Keys

Edit `backend/.env` and add your API keys:

#### 1. OpenAI API Key (for AI features)
```env
OPENAI_API_KEY=sk-your-openai-api-key
```
Get your key from: https://platform.openai.com/api-keys

#### 2. Google APIs (Calendar & Gmail)
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

To get Google credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API and Gmail API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`
6. Copy the Client ID and Client Secret

#### 3. Canvas LMS API Key (for course integration)
```env
CANVAS_API_URL=https://canvas.instructure.com/api/v1
CANVAS_API_KEY=your-canvas-api-token
```

To get Canvas API key:
1. Log in to your Canvas account
2. Go to Account → Settings
3. Scroll to "Approved Integrations"
4. Click "+ New Access Token"
5. Give it a purpose and generate
6. Copy the token immediately (you won't see it again)

#### 4. Notion API Key (for task integration)
```env
NOTION_API_KEY=secret_your-notion-integration-key
```

To get Notion integration key:
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "+ New integration"
3. Give it a name and select associated workspace
4. Copy the "Internal Integration Token"
5. Share your databases with the integration

#### 5. Health Data APIs (optional)

**Google Fit:**
```env
GOOGLE_FIT_CLIENT_ID=your-fit-client-id
GOOGLE_FIT_CLIENT_SECRET=your-fit-client-secret
```
Use the same Google Cloud project and enable Google Fit API

**Apple Health:**
```env
APPLE_HEALTH_KEY=your-apple-health-key
```
Note: Apple Health requires an iOS app with HealthKit integration

### Optional Configuration

```env
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database (if using different credentials)
DATABASE_URL=postgresql://circa_user:circa_password@localhost:5432/circa_db

# Redis (if using different host)
REDIS_URL=redis://localhost:6379/0
```

## Database Migrations

If you make changes to the database models:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing the Setup

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 2. Check API Documentation
Visit http://localhost:8000/docs to see interactive API documentation

### 3. Test Frontend
Open http://localhost:3000 in your browser and try:
- Registering a new account
- Logging in
- Completing the onboarding quiz
- Exploring the dashboard

### 4. Test Integrations
1. Go to Integrations page
2. Connect Canvas LMS with your API key
3. Click "Sync Now" to import assignments
4. Check Tasks page to see imported items

## Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Type checking
mypy app/

# Format code
black app/
isort app/
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Run linter
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Using Docker

```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Production Setup

1. **Set environment variables:**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Use production database credentials
   - Configure proper CORS origins

2. **Backend:**
   ```bash
   # Install production server
   pip install gunicorn
   
   # Run with Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Frontend:**
   ```bash
   npm run build
   # Serve the dist/ folder with nginx or similar
   ```

4. **Database:**
   - Run migrations: `alembic upgrade head`
   - Set up regular backups

5. **Background Jobs:**
   ```bash
   # Start Celery worker
   celery -A app.celery_worker worker --loglevel=info
   
   # Optional: Start Celery beat for scheduled tasks
   celery -A app.celery_worker beat --loglevel=info
   ```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
# Or use a different port
uvicorn app.main:app --port 8001
```

**Database connection errors:**
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Ensure database exists: `psql -l`

**Redis connection errors:**
- Check Redis is running: `redis-cli ping`
- Should return: `PONG`

**Import errors:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**Module not found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 already in use:**
```bash
# Use different port
npm run dev -- --port 3001
```

**API connection errors:**
- Check backend is running
- Verify `VITE_API_URL` in `.env`
- Check browser console for CORS errors

## Next Steps

1. **Complete Onboarding:** Answer the quiz to personalize your experience
2. **Connect Integrations:** Link your Google Calendar, Canvas, etc.
3. **Set Preferences:** Configure your sleep schedule, study habits, and fitness goals
4. **Let AI Work:** The system will learn from your patterns and optimize scheduling

## Getting Help

- **Documentation:** See README.md for project overview
- **API Docs:** http://localhost:8000/docs
- **Issues:** Check existing issues or create a new one

## Security Notes

⚠️ **Important for Production:**

1. Never commit `.env` files to version control
2. Use strong, random `SECRET_KEY`
3. Use HTTPS in production
4. Rotate API keys regularly
5. Set up proper CORS origins
6. Enable database backups
7. Use environment-specific configurations
8. Keep dependencies updated

---

Happy scheduling with Circa! 🎯

