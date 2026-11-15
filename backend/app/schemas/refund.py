import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RefundIssueCategory, RefundStatus


class RefundRequestCreate(BaseModel):
    order_id: uuid.UUID = Field(..., description="ID of the eligible delivered order")
    issue_category: RefundIssueCategory = Field(..., description="Category of the issue")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed explanation of the issue")
    requested_amount: Decimal = Field(..., gt=0, decimal_places=2, description="Requested refund amount in INR")


class RefundApproveRequest(BaseModel):
    approved_amount: Decimal = Field(..., gt=0, decimal_places=2, description="Approved refund amount in INR")
    resolution_notes: Optional[str] = Field(None, max_length=1000, description="Notes on resolution / settlement")


class RefundRejectRequest(BaseModel):
    explanation: str = Field(..., min_length=5, max_length=1000, description="Mandatory explanation for rejection")


class RefundResolveRequest(BaseModel):
    resolution_notes: Optional[str] = Field(None, max_length=1000, description="Final settlement confirmation notes")


class RefundRequestResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: Optional[str] = None
    restaurant_id: uuid.UUID
    restaurant_name: Optional[str] = None
    issue_category: str
    description: str
    requested_amount: Decimal
    approved_amount: Optional[Decimal] = None
    status: str
    owner_response: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RefundListResponse(BaseModel):
    requests: List[RefundRequestResponse]
    total: int

