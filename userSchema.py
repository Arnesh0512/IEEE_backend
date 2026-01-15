from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Literal

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    college_or_university: str
    course: str
    year: Literal[1, 2, 3, 4]
    github_profile: Optional[HttpUrl] = None
    linkedin_profile: Optional[HttpUrl] = None
