# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.event import Event
from app.models.task import Task
from app.models.integration import Integration
from app.models.preference import UserPreference
from app.models.health_data import HealthData
from app.models.quiz_response import QuizResponse

__all__ = [
    "User",
    "Event",
    "Task",
    "Integration",
    "UserPreference",
    "HealthData",
    "QuizResponse",
]

