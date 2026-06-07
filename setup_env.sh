#!/bin/bash

# Setup script for Circa environment variables.
# Fill in your own credentials below, then run: ./setup_env.sh
# This file is a template — it contains NO real secrets. The generated
# backend/.env and frontend/.env are gitignored.

echo "Setting up Circa environment..."

# Create backend .env
cat > backend/.env << 'EOF'
# Application
APP_NAME=Circa
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=change-me-to-a-long-random-string
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://circa_user:circa_password@localhost:5432/circa_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# OpenAI (optional — only needed for the LLM-assisted import/scheduler)
OPENAI_API_KEY=your-openai-api-key

# Google APIs (optional — only needed for Google Calendar sync)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Canvas LMS (optional — manual import works without this)
CANVAS_API_URL=https://canvas.instructure.com/api/v1
CANVAS_API_KEY=

# Notion (optional)
NOTION_API_KEY=
NOTION_VERSION=2022-06-28

# Health APIs (optional)
APPLE_HEALTH_KEY=
GOOGLE_FIT_CLIENT_ID=
GOOGLE_FIT_CLIENT_SECRET=

# Gmail (optional)
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOF

# Create frontend .env
cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Circa
EOF

echo "Environment files created. Edit backend/.env to add any optional API keys."
echo "Next: docker-compose up -d  ->  http://localhost:3000"
