import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KuaDocumentBase(BaseModel):
    owner_type: Literal["cpp", "cpw", "both"] = "both"
    document_key: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    is_required: bool = True
    status: Literal["belum", "sudah", "diverifikasi"] = "belum"
    file_url: str | None = Field(default=None, max_length=500)
    expiry_date: date | None = None


class KuaDocumentUpdate(BaseModel):
    status: Literal["belum", "sudah", "diverifikasi"] | None = None
    file_url: str | None = Field(default=None, max_length=500)
    expiry_date: date | None = None


class KuaDocumentResponse(KuaDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
