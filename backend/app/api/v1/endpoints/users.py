from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.preference import UserPreference
from app.schemas.user import UserResponse, UserUpdate
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        from app.core.security import get_password_hash
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/me/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences"""
    result = await db.execute(
        select(UserPreference).filter(UserPreference.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)
    
    return preferences


@router.put("/me/preferences")
async def update_user_preferences(
    preferences_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    result = await db.execute(
        select(UserPreference).filter(UserPreference.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
    
    for field, value in preferences_data.items():
        if hasattr(preferences, field):
            setattr(preferences, field, value)
    
    await db.commit()
    await db.refresh(preferences)
    
    return preferences

