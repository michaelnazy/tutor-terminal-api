from pydantic import BaseModel
from typing import Optional

# ==========================================
# COURSE SCHEMAS
# ==========================================
class CourseCreate(BaseModel):
    course_name: str
    course_code: str
    professor_email: str
    room_number: Optional[str] = None

class Course(CourseCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# MODULE SCHEMAS
# ==========================================
class ModuleCreate(BaseModel):
    due_date: str
    title: str
    progress_percentage: float

class ModuleResponse(ModuleCreate):
    id: int
    course_id: int

    class Config:
        from_attributes = True