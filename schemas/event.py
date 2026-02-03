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
    last_date_to_register: Optional[date] = None

    event_capacity: Optional[int] = None
    event_type: Optional[Literal["Free", "Paid"]] = None
    event_team_allowed: Optional[bool] = None
    event_team_size: Optional[int] = None

    venue: Optional[str] = None
    person_incharge: Optional[str] = None

    event_status: Optional[Literal["Ongoing", "Completed"]] = None

    event_prizes: Optional[str] = None

    @classmethod
    def convert_to_form(
        cls,
        event_name: str = Form(...),
        event_description: Optional[str] = Form(None),
        event_date: Optional[date] = Form(None),
        event_time: Optional[time] = Form(None),
        duration: Optional[str] = Form(None),
        last_date_to_register: Optional[date] = Form(None),
        event_capacity: Optional[int] = Form(None),
        event_type: Optional[Literal["Free", "Paid"]] = Form(None),
        event_team_allowed: Optional[bool] = Form(None),
        event_team_size: Optional[int] = Form(None),
        venue: Optional[str] = Form(None),
        person_incharge: Optional[str] = Form(None),
        event_status: Optional[Literal["Ongoing", "Completed"]] = Form(None),
        event_prizes: Optional[str] = Form(None),
    ):
        return cls(
            event_name=event_name,
            event_description=event_description,
            event_date=event_date,
            event_time=event_time,
            duration=duration,
            last_date_to_register=last_date_to_register,
            event_capacity=event_capacity,
            event_type=event_type,
            event_team_allowed=event_team_allowed,
            event_team_size=event_team_size,
            venue=venue,
            person_incharge=person_incharge,
            event_status=event_status,
            event_prizes=event_prizes,
        )
