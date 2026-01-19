from pydantic import BaseModel
from typing import Literal, Optional
from datetime import date,time
from fastapi import Form


class EventCreate(BaseModel):
    event_name: str  # REQUIRED

    event_description: Optional[str] = None

    event_date: Optional[date] = None
    event_time: Optional[time] = None
    duration: Optional[str] = None

    event_type: Optional[Literal["Free", "Paid"]] = None
    event_team_allowed: Optional[bool] = None

    venue: Optional[str] = None
    person_incharge: Optional[str] = None

    event_status: Optional[Literal["Ongoing", "Completed"]] = None

    @classmethod
    def convert_to_form(
        cls,
        event_name: str = Form(...),
        event_description: Optional[str] = Form(None),
        event_date: Optional[date] = Form(None),
        event_time: Optional[time] = Form(None),
        duration: Optional[str] = Form(None),
        event_type: Optional[Literal["free", "paid"]] = Form(None),
        event_team_allowed: Optional[bool] = Form(None),
        venue: Optional[str] = Form(None),
        person_incharge: Optional[str] = Form(None),
        event_status: Optional[Literal["Ongoing", "Completed"]] = Form(None),
    ):
        return cls(
            event_name=event_name,
            event_description=event_description,
            event_date=event_date,
            event_time=event_time,
            duration=duration,
            event_type=event_type,
            event_team_allowed=event_team_allowed,
            venue=venue,
            person_incharge=person_incharge,
            event_status=event_status,
        )
