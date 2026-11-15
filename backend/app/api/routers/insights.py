from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_customer
from app.schemas.insights import (
    SpendingSummaryResponse,
    OrderingPatternsResponse,
    RecommendationsResponse,
    AiNarrativeResponse,
)
from app.services import insights_service

router = APIRouter(prefix="/insights", tags=["AI Order Insights"])


@router.get(
    "/summary",
    response_model=SpendingSummaryResponse,
    summary="Get Customer Spending Analysis",
    description="Computes total spend, average order value, completed deliveries, and monthly spending trends.",
)
def get_spending_summary_endpoint(
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return insights_service.get_spending_summary(db=db, customer_id=current_user.id)


@router.get(
    "/patterns",
    response_model=OrderingPatternsResponse,
    summary="Get Ordering Patterns & Habits",
    description="Identifies top dishes, favourite restaurants, top food categories, and order frequency.",
)
def get_ordering_patterns_endpoint(
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return insights_service.get_ordering_patterns(db=db, customer_id=current_user.id)


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get Personalized Dish Recommendations",
    description="Suggests dishes based on preferred categories and popular campus items.",
)
def get_recommendations_endpoint(
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return insights_service.get_personalized_recommendations(db=db, customer_id=current_user.id)


@router.get(
    "/ai-summary",
    response_model=AiNarrativeResponse,
    summary="Get AI-Powered Dining Insights Narrative",
    description="Generates an energetic AI summary of student dining habits via Gemini, with rule-based fallback.",
)
def get_ai_narrative_endpoint(
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return insights_service.get_ai_insights_narrative(
        db=db, customer_id=current_user.id, user_name=current_user.full_name
    )

