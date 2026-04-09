from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# We moved Base over here so main.py and models.py stop fighting!
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)

    # This creates a virtual link to see all lessons for a specific student
    lessons = relationship("Lesson", back_populates="student")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hourly_rate = Column(Integer)

    lessons = relationship("Lesson", back_populates="subject")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(Date)
    time = Column(Time)
    duration_minutes = Column(Integer)
    status = Column(String, default="Upcoming") # Upcoming, Completed, Canceled

    # These link back to the parent tables
    student = relationship("Student", back_populates="lessons")
    subject = relationship("Subject", back_populates="lessons")
    # This links to the child table (Notes)
    notes = relationship("Note", back_populates="lesson")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="notes")