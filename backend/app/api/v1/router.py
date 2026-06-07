from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, events, tasks, integrations, dashboard, ai, manual_import, google_oauth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(manual_import.router, prefix="/manual-import", tags=["manual-import"])
api_router.include_router(google_oauth.router, prefix="/google", tags=["google-oauth"])

