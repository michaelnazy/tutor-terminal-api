# ... (Keep imports and DB setup from before)

# Create an Exam for a Course
@app.post("/courses/{course_id}/exams/", response_model=schemas.ExamResponse)
def create_exam(course_id: int, exam: schemas.ExamCreate, db: Session = Depends(get_db)):
    new_exam = models.Exam(**exam.dict(), course_id=course_id)
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam

# Get all Exams for a Course
@app.get("/courses/{course_id}/exams/", response_model=List[schemas.ExamResponse])
def get_exams(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Exam).filter(models.Exam.course_id == course_id).all()

# Create a Module for an Exam
@app.post("/exams/{exam_id}/modules/", response_model=schemas.ModuleResponse)
def create_module(exam_id: int, module: schemas.ModuleBase, db: Session = Depends(get_db)):
    new_module = models.ModuleModel(**module.dict(), exam_id=exam_id)
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

# Get all Modules for an Exam
@app.get("/exams/{exam_id}/modules/", response_model=List[schemas.ModuleResponse])
def get_modules(exam_id: int, db: Session = Depends(get_db)):
    return db.query(models.ModuleModel).filter(models.ModuleModel.exam_id == exam_id).all()

# Update module progress
@app.put("/modules/{module_id}")
def update_progress(module_id: int, progress: float, db: Session = Depends(get_db)):
    db_module = db.query(models.ModuleModel).filter(models.ModuleModel.id == module_id).first()
    db_module.progress_percentage = progress
    db.commit()
    return {"status": "updated"}