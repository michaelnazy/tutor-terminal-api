from pydantic import BaseModel
from typing import List, Optional

class ModuleBase(BaseModel):
    title: str
    progress_percentage: float = 0.0

class ModuleResponse(ModuleBase):
    id: int
    exam_id: int
    class Config: from_attributes = True

class ExamCreate(BaseModel):
    exam_name: str
    exam_date: str

class ExamResponse(ExamCreate):
    id: int
    course_id: int
    class Config: from_attributes = True

class CourseCreate(BaseModel):
    course_name: str
    course_code: str
    room_number: str

class CourseResponse(CourseCreate):
    id: int
    class Config: from_attributes = True

class FlashcardBase(BaseModel):
    question: str
    answer: str

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardResponse(FlashcardBase):
    id: int

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class NotesRequest(BaseModel):
    text: str

