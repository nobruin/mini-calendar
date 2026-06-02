from datetime import datetime, date, time
from sqlalchemy.orm import Session
from . import models, schemas


def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event(db: Session, event_id: int) -> models.Event | None:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(
    db: Session,
    filter_date: date | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[models.Event]:
    query = db.query(models.Event)

    if filter_date:
        day_start = datetime.combine(filter_date, time.min)
        day_end = datetime.combine(filter_date, time.max)
        query = query.filter(
            models.Event.start_datetime >= day_start,
            models.Event.start_datetime <= day_end,
        )
    else:
        if start_date:
            query = query.filter(
                models.Event.start_datetime >= datetime.combine(start_date, time.min)
            )
        if end_date:
            query = query.filter(
                models.Event.start_datetime <= datetime.combine(end_date, time.max)
            )

    return query.order_by(models.Event.start_datetime).all()


def update_event(
    db: Session, event_id: int, event_data: schemas.EventUpdate
) -> models.Event | None:
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    for key, value in event_data.model_dump(exclude_unset=True).items():
        setattr(db_event, key, value)
    db_event.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_event)
    return db_event


def cancel_event(db: Session, event_id: int) -> models.Event | None:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    db_event.status = "cancelled"
    db_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> bool:
    db_event = get_event(db, event_id)
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True
