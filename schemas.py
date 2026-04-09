from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time, datetime

# ==========================================
# STUDENT SCHEMAS
# ==========================================
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

class Student(StudentCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# SUBJECT SCHEMAS
# ==========================================
class SubjectCreate(BaseModel):
    name: str
    hourly_rate: int

class Subject(SubjectCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# LESSON SCHEMAS
# ==========================================
class LessonCreate(BaseModel):
    student_id: int
    subject_id: int
    date: date
    time: time
    duration_minutes: int

class Lesson(LessonCreate):
    id: int
    status: str

    class Config:
        from_attributes = True

# ==========================================
# UPDATE SCHEMAS
# ==========================================
class LessonUpdate(BaseModel):
    status: str

# ==========================================
# NOTE SCHEMAS (Phase 6)
# ==========================================
class NoteCreate(BaseModel):
    content: str

class Note(NoteCreate):
    id: int
    lesson_id: int
    created_at: datetime

    class Config:
        from_attributes = True