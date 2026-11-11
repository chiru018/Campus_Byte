import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery_partner import DeliveryPartner
from app.models.enums import VehicleType


def get_delivery_partner_by_user_id(
    db: Session, user_id: uuid.UUID
) -> Optional[DeliveryPartner]:
    return db.scalar(
        select(DeliveryPartner).where(DeliveryPartner.user_id == user_id)
    )


def create_delivery_partner_profile(
    db: Session,
    user_id: uuid.UUID,
    vehicle_type: VehicleType = VehicleType.BICYCLE,
) -> DeliveryPartner:
    partner = DeliveryPartner(
        user_id=user_id,
        vehicle_type=vehicle_type,
        is_available=True,
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner
