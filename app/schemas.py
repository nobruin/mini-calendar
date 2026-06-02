from datetime import datetime
from pydantic import BaseModel, model_validator


class EventBase(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    start_datetime: datetime
    end_datetime: datetime

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "EventBase":
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "EventUpdate":
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValueError("end_datetime must be after start_datetime")
        return self


class EventResponse(EventBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
