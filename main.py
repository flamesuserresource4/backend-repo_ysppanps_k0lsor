import os
import secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import (
    Teacher, Student, Subject, Lecture, Exam, Grade,
    CreateStudent, CreateSubject, CreateLecture, CreateExam, CreateGrade,
    NewsletterSubscriber, CreateNewsletterSubscribe,
)

app = FastAPI(title="TeachEase API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "TeachEase Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Utility to convert ObjectId to string in responses

def serialize_docs(docs: List[dict]):
    out = []
    for d in docs:
        d = dict(d)
        if d.get("_id"):
            d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


# Teachers (basic create/list)
class CreateTeacher(BaseModel):
    name: str
    email: str
    department: Optional[str] = None

@app.post("/teachers")
def create_teacher(payload: CreateTeacher):
    teacher = Teacher(**payload.model_dump())
    tid = create_document("teacher", teacher)
    return {"id": tid}

@app.get("/teachers")
def list_teachers():
    docs = get_documents("teacher", {})
    return serialize_docs(docs)


# Students
@app.post("/students")
def create_student(payload: CreateStudent):
    student = Student(**payload.model_dump())
    sid = create_document("student", student)
    return {"id": sid}

@app.get("/students")
def list_students(class_name: Optional[str] = None):
    filt = {"class_name": class_name} if class_name else {}
    docs = get_documents("student", filt)
    return serialize_docs(docs)


# Subjects
@app.post("/subjects")
def create_subject(payload: CreateSubject):
    subject = Subject(**payload.model_dump())
    sid = create_document("subject", subject)
    return {"id": sid}

@app.get("/subjects")
def list_subjects():
    docs = get_documents("subject", {})
    return serialize_docs(docs)


# Lectures
@app.post("/lectures")
def create_lecture(payload: CreateLecture):
    lecture = Lecture(**payload.model_dump())
    lid = create_document("lecture", lecture)
    return {"id": lid}

@app.get("/lectures")
def list_lectures(subject_code: Optional[str] = None):
    filt = {"subject_code": subject_code} if subject_code else {}
    docs = get_documents("lecture", filt)
    return serialize_docs(docs)


# Exams
@app.post("/exams")
def create_exam(payload: CreateExam):
    exam = Exam(**payload.model_dump())
    eid = create_document("exam", exam)
    return {"id": eid}

@app.get("/exams")
def list_exams(subject_code: Optional[str] = None):
    filt = {"subject_code": subject_code} if subject_code else {}
    docs = get_documents("exam", filt)
    return serialize_docs(docs)


# Grades
@app.post("/grades")
def create_grade(payload: CreateGrade):
    grade = Grade(**payload.model_dump())
    gid = create_document("grade", grade)
    return {"id": gid}

@app.get("/grades")
def list_grades(roll_number: Optional[str] = None, subject_code: Optional[str] = None):
    filt = {}
    if roll_number:
        filt["roll_number"] = roll_number
    if subject_code:
        filt["subject_code"] = subject_code
    docs = get_documents("grade", filt)
    return serialize_docs(docs)


# Newsletter (double opt-in)
@app.post("/newsletter/subscribe")
def newsletter_subscribe(payload: CreateNewsletterSubscribe):
    token = secrets.token_urlsafe(24)
    sub = NewsletterSubscriber(email=payload.email, status="pending", token=token)
    sid = create_document("newslettersubscriber", sub)
    backend_base = os.getenv("BACKEND_URL") or ""
    confirm_url = f"{backend_base}/newsletter/confirm?token={token}"
    return {"id": sid, "status": "pending", "confirm_url": confirm_url}

@app.get("/newsletter/confirm")
def newsletter_confirm(token: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = db["newslettersubscriber"].find_one({"token": token})
    if not doc:
        raise HTTPException(status_code=404, detail="Invalid token")
    db["newslettersubscriber"].update_one({"_id": doc["_id"]}, {"$set": {"status": "confirmed", "confirmed_at": __import__('datetime').datetime.utcnow()}})
    return {"status": "confirmed"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
