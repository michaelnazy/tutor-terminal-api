from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import schemas, models
import os
from dotenv import load_dotenv
from typing import List

# --- NEW AI IMPORTS ---
import google.generativeai as genai
import json
from pydantic import BaseModel

load_dotenv()

# THE ENGINE
app = FastAPI(title="Student Survival API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# --- AI CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Define what the incoming AI request looks like
class NotesRequest(BaseModel):
    text: str

# DATABASE SETUP
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This creates the new tables automatically
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
    return db.query(models.ModuleModel).filter(models.ModuleModel.exam_id == exam_id).all()

@app.put("/modules/{module_id}")
def update_progress(module_id: int, progress: float, db: Session = Depends(get_db)):
    db_module = db.query(models.ModuleModel).filter(models.ModuleModel.id == module_id).first()
    if db_module:
        db_module.progress_percentage = progress
        db.commit()
        return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Module not found")


# ==========================================
# 4. AI ROUTES
# ==========================================

@app.post("/generate-flashcards/")
async def generate_flashcards(req: NotesRequest):
    if not GEMINI_API_KEY:
        return {"error": "API key missing on server"}
    
    try:
        # Load the Gemini AI model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Give the AI strict instructions
        prompt = f"""
        You are an expert tutor. Create 5 study flashcards from these notes.
        Respond ONLY with a valid JSON array of objects. Each object must have exactly two keys: 'question' and 'answer'. 
        Do not include markdown formatting like ```json.
        
        Notes:
        {req.text}
        """
        
        response = model.generate_content(prompt)
        
        # Convert the AI's text response into a real JSON object
        flashcards = json.loads(response.text.strip())
        return {"flashcards": flashcards}
        
    except Exception as e:
        return {"error": str(e)}