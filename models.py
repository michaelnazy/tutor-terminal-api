from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    course_code = Column(String)
    room_number = Column(String)
    
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    exam_name = Column(String) # e.g., "Midterm"
    exam_date = Column(String) # e.g., "May 10"
    
    course = relationship("Course", back_populates="exams")
    modules = relationship("ModuleModel", back_populates="exam", cascade="all, delete-orphan")

class ModuleModel(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"))
    title = Column(String)
    progress_percentage = Column(Float, default=0.0)

    exam = relationship("Exam", back_populates="modules")