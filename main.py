from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import schemas, models
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Student Survival API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("FATAL ERROR: DATABASE_URL not found in .env file!")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This automatically creates the new 'courses' and 'modules' tables in Neon!
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Student Hub Brain is Active"}

# ==========================================
# COURSE ROUTES
# ==========================================
@app.get("/courses/", response_model=list[schemas.Course])
def get_all_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted."}

# ==========================================
# MODULE ROUTES
# ==========================================
@app.post("/courses/{course_id}/modules/", response_model=schemas.ModuleResponse)
def create_module(course_id: int, module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    new_module = models.ModuleModel(**module.dict(), course_id=course_id)
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

@app.get("/courses/{course_id}/modules/", response_model=list[schemas.ModuleResponse])
def get_modules(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.ModuleModel).filter(models.ModuleModel.course_id == course_id).all()