import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VendorBase(BaseModel):
    vendor_name: str = Field(min_length=1, max_length=255)
    category: Literal[
        "venue",
        "catering",
        "dekorasi",
        "mua",
        "dokumentasi",
        "hiburan",
        "souvenir",
        "undangan",
        "lainnya",
    ] = "lainnya"
    contact_wa: str | None = Field(default=None, max_length=50)
    total_amount: int = Field(default=0, ge=0)
    dp_amount: int = Field(default=0, ge=0)
    paid_amount: int = Field(default=0, ge=0)
    status: Literal["belum_bayar", "dp", "lunas"] = "belum_bayar"
    due_date: date | None = None
    invoice_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    vendor_name: str | None = Field(default=None, min_length=1, max_length=255)
    category: Literal[
        "venue",
        "catering",
        "dekorasi",
        "mua",
        "dokumentasi",
        "hiburan",
        "souvenir",
        "undangan",
        "lainnya",
    ] | None = None
    contact_wa: str | None = Field(default=None, max_length=50)
    total_amount: int | None = Field(default=None, ge=0)
    dp_amount: int | None = Field(default=None, ge=0)
    paid_amount: int | None = Field(default=None, ge=0)
    status: Literal["belum_bayar", "dp", "lunas"] | None = None
    due_date: date | None = None
    invoice_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class VendorResponse(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
