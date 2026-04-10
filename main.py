from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import schemas, models
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

# THE ENGINE: This is the 'app' the error was complaining about!
app = FastAPI(title="Student Survival API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# DATABASE SETUP
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This creates the new Exams table automatically
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Student Hub API is running!"}

# ==========================================
# 1. COURSE ROUTES
# ==========================================

@app.get("/courses/", response_model=List[schemas.CourseResponse])
def get_all_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.post("/courses/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
    return {"message": "Deleted"}

# ==========================================
# 2. EXAM ROUTES (The new middle layer)
# ==========================================

@app.post("/courses/{course_id}/exams/", response_model=schemas.ExamResponse)
def create_exam(course_id: int, exam: schemas.ExamCreate, db: Session = Depends(get_db)):
    new_exam = models.Exam(**exam.dict(), course_id=course_id)
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam

@app.get("/courses/{course_id}/exams/", response_model=List[schemas.ExamResponse])
def get_exams(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Exam).filter(models.Exam.course_id == course_id).all()

# ==========================================
# 3. MODULE ROUTES
# ==========================================

@app.post("/exams/{exam_id}/modules/", response_model=schemas.ModuleResponse)
def create_module(exam_id: int, module: schemas.ModuleBase, db: Session = Depends(get_db)):
    new_module = models.ModuleModel(**module.dict(), exam_id=exam_id)
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

@app.get("/exams/{exam_id}/modules/", response_model=List[schemas.ModuleResponse])
def get_modules(exam_id: int, db: Session = Depends(get_db)):
    return db.query(models.ModuleModel).filter(models.ModuleModel.id == exam_id).all()

@app.put("/modules/{module_id}")
def update_progress(module_id: int, progress: float, db: Session = Depends(get_db)):
    db_module = db.query(models.ModuleModel).filter(models.ModuleModel.id == module_id).first()
    if db_module:
        db_module.progress_percentage = progress
        db.commit()
        return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Module not found")