from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.integration import Integration
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all integrations for the current user"""
    result = await db.execute(
        select(Integration).filter(Integration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    
    # Don't expose tokens
    return [{
        "id": i.id,
        "provider": i.provider,
        "is_active": i.is_active,
        "sync_enabled": i.sync_enabled,
        "last_sync_at": i.last_sync_at,
        "created_at": i.created_at
    } for i in integrations]


@router.post("/google/connect")
async def connect_google(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect Google Calendar and Gmail"""
    # TODO: Implement OAuth flow
    return {"message": "Google integration OAuth flow to be implemented"}


@router.post("/canvas/connect")
async def connect_canvas(
    api_key: str,
    canvas_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect Canvas LMS"""
    # Check if integration already exists
    result = await db.execute(
        select(Integration).filter(
            and_(
                Integration.user_id == current_user.id,
                Integration.provider == "canvas"
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        integration.access_token = api_key
        integration.config = {"canvas_url": canvas_url}
        integration.is_active = True
    else:
        integration = Integration(
            user_id=current_user.id,
            provider="canvas",
            access_token=api_key,
            is_active=True,
            config={"canvas_url": canvas_url}
        )
        db.add(integration)
    
    await db.commit()
    await db.refresh(integration)
    
    return {"message": "Canvas integration connected successfully"}


@router.post("/notion/connect")
async def connect_notion(
    api_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect Notion"""
    result = await db.execute(
        select(Integration).filter(
            and_(
                Integration.user_id == current_user.id,
                Integration.provider == "notion"
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        integration.access_token = api_key
        integration.is_active = True
    else:
        integration = Integration(
            user_id=current_user.id,
            provider="notion",
            access_token=api_key,
            is_active=True
        )
        db.add(integration)
    
    await db.commit()
    await db.refresh(integration)
    
    return {"message": "Notion integration connected successfully"}


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a sync for a specific integration"""
    result = await db.execute(
        select(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.user_id == current_user.id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # TODO: Trigger background sync task
    from datetime import datetime
    integration.last_sync_at = datetime.utcnow()
    await db.commit()
    
    return {"message": f"Sync triggered for {integration.provider}"}


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect an integration"""
    result = await db.execute(
        select(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.user_id == current_user.id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    await db.delete(integration)
    await db.commit()
    
    return {"message": "Integration disconnected successfully"}

