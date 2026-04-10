from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ==========================================
# 1. COURSES (Formerly Students)
# ==========================================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, index=True)       # e.g., "Intro to Python"
    course_code = Column(String, index=True)       # e.g., "CS101"
    professor_email = Column(String, index=True)   
    room_number = Column(String)                   

    # Link to the syllabus modules
    modules = relationship("ModuleModel", back_populates="course", cascade="all, delete-orphan")

# ==========================================
# 2. SYLLABUS MODULES (Formerly Sessions)
# ==========================================
class ModuleModel(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    
    due_date = Column(String(50), nullable=False)         # e.g., "April 15"
    title = Column(String(255), nullable=False)           # e.g., "Week 4: GUI Systems"
    progress_percentage = Column(Float, nullable=False)   # e.g., 40.0 (for 40%)

    # Link back to the course
    course = relationship("Course", back_populates="modules")