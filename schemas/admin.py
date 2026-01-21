from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Literal, List

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    team: str
    role: str
    phone_number: str
    college_or_university: str
    course: str
    year: Literal[1, 2, 3, 4]
    gender: Literal["M", "F", "O"]
    github_profile: Optional[HttpUrl] = None
    linkedin_profile: Optional[HttpUrl] = None