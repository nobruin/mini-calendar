import calendar
from datetime import date, datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _adjacent_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    if month > 12:
        return year + 1, 1
    if month < 1:
        return year - 1, 12
    return year, month


@router.get("/", response_class=HTMLResponse)
def calendar_view(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
):
    today = date.today()
    year = year or today.year
    month = month or today.month

    weeks = calendar.monthcalendar(year, month)
    last_day = calendar.monthrange(year, month)[1]

    events = crud.get_events(db, start_date=date(year, month, 1), end_date=date(year, month, last_day))

    events_by_day: dict[int, list] = {}
    for ev in events:
        events_by_day.setdefault(ev.start_datetime.day, []).append(ev)

    prev_year, prev_month = _adjacent_month(year, month, -1)
    next_year, next_month = _adjacent_month(year, month, 1)

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "year": year,
        "month": month,
        "month_name": MONTH_NAMES[month],
        "weeks": weeks,
        "events_by_day": events_by_day,
        "today": today,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    })


@router.get("/events/new", response_class=HTMLResponse)
def new_event_form(request: Request):
    return templates.TemplateResponse("event_form.html", {
        "request": request,
        "event": None,
        "error": None,
        "form_data": None,
    })


@router.post("/events")
async def create_event(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    start_datetime: str = Form(...),
    end_datetime: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        event_data = schemas.EventCreate(
            title=title,
            description=description or None,
            location=location or None,
            start_datetime=datetime.fromisoformat(start_datetime),
            end_datetime=datetime.fromisoformat(end_datetime),
        )
        crud.create_event(db, event_data)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("event_form.html", {
            "request": request,
            "event": None,
            "error": str(e),
            "form_data": {
                "title": title,
                "description": description,
                "location": location,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
            },
        })


@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("event_detail.html", {
        "request": request,
        "event": event,
    })


@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
def edit_event_form(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id)
    if not event:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("event_form.html", {
        "request": request,
        "event": event,
        "error": None,
        "form_data": None,
    })


@router.post("/events/{event_id}/edit")
async def update_event(
    request: Request,
    event_id: int,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    start_datetime: str = Form(...),
    end_datetime: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        event_data = schemas.EventUpdate(
            title=title,
            description=description or None,
            location=location or None,
            start_datetime=datetime.fromisoformat(start_datetime),
            end_datetime=datetime.fromisoformat(end_datetime),
        )
        updated = crud.update_event(db, event_id, event_data)
        if not updated:
            return RedirectResponse(url="/", status_code=303)
        return RedirectResponse(url=f"/events/{event_id}", status_code=303)
    except Exception as e:
        event = crud.get_event(db, event_id)
        return templates.TemplateResponse("event_form.html", {
            "request": request,
            "event": event,
            "error": str(e),
            "form_data": None,
        })


@router.post("/events/{event_id}/cancel")
def cancel_event(event_id: int, db: Session = Depends(get_db)):
    crud.cancel_event(db, event_id)
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


@router.post("/events/{event_id}/delete")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    crud.delete_event(db, event_id)
    return RedirectResponse(url="/", status_code=303)
