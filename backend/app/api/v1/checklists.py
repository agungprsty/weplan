import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.checklist import (
    ChecklistCreate,
    ChecklistResponse,
    ChecklistUpdate,
)
from app.services import checklist as checklist_service

router = APIRouter()


@router.get("/", response_model=list[ChecklistResponse])
async def list_checklists(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[ChecklistResponse]:
    return await checklist_service.list_checklists(db, wedding_id)


@router.post("/", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    wedding_id: uuid.UUID,
    data: ChecklistCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    return await checklist_service.create_checklist(db, wedding_id, data)


@router.patch("/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    data: ChecklistUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    checklist = await checklist_service.update_checklist(
        db, wedding_id, checklist_id, data
    )
    if checklist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    return checklist


@router.get("/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    checklist = await checklist_service.get_checklist(db, wedding_id, checklist_id)
    if checklist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    return checklist


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> None:
    checklist = await checklist_service.get_checklist(db, wedding_id, checklist_id)
    if checklist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    await db.delete(checklist)
