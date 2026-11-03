from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps import Services, services
from ..services.feedback import FEEDBACK_ID, FeedbackError

router = APIRouter(tags=["feedback"])


class Rating(BaseModel):
    faithful: str | None = None
    complete: str | None = None
    should_have_answered: str | None = None


class FeedbackIn(BaseModel):
    answer: dict                      # the /ask result being rated (plus k)
    rating: Rating
    comment: str | None = Field(None, max_length=4000)


@router.get("/feedback")
def list_feedback(svc: Services = Depends(services)) -> dict:
    items = svc.feedback.all()
    return {"items": items, "summary": svc.feedback.summary(), "file": str(svc.feedback.path)}


@router.post("/feedback")
def add_feedback(body: FeedbackIn, svc: Services = Depends(services)) -> dict:
    try:
        return svc.feedback.save(body.answer, body.rating.model_dump(), body.comment)
    except FeedbackError as exc:
        raise HTTPException(400, str(exc))


@router.put("/feedback/{feedback_id}")
def update_feedback(feedback_id: str, body: FeedbackIn, svc: Services = Depends(services)) -> dict:
    if not FEEDBACK_ID.match(feedback_id):
        raise HTTPException(404, f"No rating {feedback_id}")
    try:
        return svc.feedback.save(body.answer, body.rating.model_dump(), body.comment, feedback_id)
    except FeedbackError as exc:
        raise HTTPException(404 if "No rating" in str(exc) else 400, str(exc))


@router.delete("/feedback/{feedback_id}")
def delete_feedback(feedback_id: str, svc: Services = Depends(services)) -> dict:
    try:
        svc.feedback.delete(feedback_id)
    except FeedbackError as exc:
        raise HTTPException(404, str(exc))
    return {"deleted": feedback_id}
