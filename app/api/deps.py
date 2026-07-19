"""FastAPI dependency injection helpers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.session import get_db

# Typed alias for route signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
