from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/events", tags=["Events API"])


@router.post("", response_model=schemas.EventResponse, status_code=201)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, event)


@router.get("", response_model=list[schemas.EventResponse])
def list_events(
    date: date | None = Query(None, description="Filter by exact date (YYYY-MM-DD)"),
    start_date: date | None = Query(None, description="Range start (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Range end (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    return crud.get_events(db, filter_date=date, start_date=start_date, end_date=end_date)


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, event_data: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = crud.update_event(db, event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    if not crud.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Event not found")


@router.patch("/{event_id}/cancel", response_model=schemas.EventResponse)
def cancel_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.cancel_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
