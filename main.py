from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import schemas, models
import os
from dotenv import load_dotenv

# ==========================================
# 0. CONFIGURATION & SECURITY
# ==========================================
load_dotenv()

app = FastAPI(title="Tutor Terminal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. DATABASE ENGINE (Neon Connection)
# ==========================================
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("FATAL ERROR: DATABASE_URL not found in .env file!")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This builds your tables in Neon automatically
models.Base.metadata.create_all(bind=engine)

# Helper function to open/close DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. SYSTEM ROUTES (Health Checks)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Tutor Terminal Brain is Active"}

@app.get("/api/health")
def health_check():
    try:
        with engine.connect() as connection:
            return {"status": "100% healthy", "database_connected": True}
    except Exception as e:
        return {"status": "Database Connection Error", "error": str(e)}

# ==========================================
# 3. STUDENT ROUTES
# ==========================================

@app.get("/students/", response_model=list[schemas.Student])
def get_all_students(db: Session = Depends(get_db)):
    """Returns a list of all students from the Neon database."""
    return db.query(models.Student).all()

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check if email exists
    db_student = db.query(models.Student).filter(models.Student.email == student.email).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = models.Student(
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        phone=student.phone
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": f"Student {student_id} erased from system."}

# --- NEW: UPDATE STUDENT ROUTE ---
@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student_update: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update their information with the new data from Flutter
    db_student.first_name = student_update.first_name
    db_student.last_name = student_update.last_name
    db_student.email = student_update.email
    db_student.phone = student_update.phone
    
    # Save the changes to Neon
    db.commit()
    db.refresh(db_student)
    return db_student

# ==========================================
# 4. SUBJECTS & LESSONS ROUTES
# ==========================================

@app.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    db_subject = db.query(models.Subject).filter(models.Subject.name == subject.name).first()
    if db_subject:
        raise HTTPException(status_code=400, detail="Subject already exists")
        
    new_subject = models.Subject(name=subject.name, hourly_rate=subject.hourly_rate)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@app.post("/lessons/", response_model=schemas.Lesson)
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    new_lesson = models.Lesson(
        student_id=lesson.student_id,
        subject_id=lesson.subject_id,
        date=lesson.date,
        time=lesson.time,
        duration_minutes=lesson.duration_minutes
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson

@app.get("/students/{student_id}/lessons/", response_model=list[schemas.Lesson])
def get_student_lessons(student_id: int, db: Session = Depends(get_db)):
    # FIXED: Now correctly filters by student_id instead of the lesson's id
    lessons = db.query(models.Lesson).filter(models.Lesson.student_id == student_id).all()
    if not lessons:
        raise HTTPException(status_code=404, detail="No lessons found")
    return lessons

# ==========================================
# 5. UPDATES & NOTES
# ==========================================

@app.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson_status(lesson_id: int, lesson_update: schemas.LessonUpdate, db: Session = Depends(get_db)):
    db_lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db_lesson.status = lesson_update.status
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@app.post("/lessons/{lesson_id}/notes/", response_model=schemas.Note)
def add_lesson_note(lesson_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    new_note = models.Note(lesson_id=lesson_id, content=note.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note