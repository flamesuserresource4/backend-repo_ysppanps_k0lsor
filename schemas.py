"""
Database Schemas for TeachEase

Each Pydantic model corresponds to a MongoDB collection (collection name is the lowercase of the class name).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Core entities

class Teacher(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    department: Optional[str] = Field(None, description="Department or subject area")
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True

class Student(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    roll_number: str = Field(..., description="Unique student roll number")
    class_name: Optional[str] = Field(None, description="e.g., Grade 8 - A")
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: str = Field("active", description="active, graduated, inactive")

class Subject(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: Optional[int] = Field(1, ge=0, le=10)

class Lecture(BaseModel):
    subject_code: str
    topic: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    teacher_email: Optional[str] = None
    duration_minutes: Optional[int] = Field(45, ge=10, le=300)

class Exam(BaseModel):
    title: str
    subject_code: str
    scheduled_at: Optional[datetime] = None
    total_marks: int = Field(100, ge=1, le=1000)

class Grade(BaseModel):
    roll_number: str
    subject_code: str
    exam_title: Optional[str] = None
    marks_obtained: float = Field(..., ge=0)
    remarks: Optional[str] = None

# Lightweight request models for simple creates via API

class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    roll_number: str
    email: Optional[str] = None
    class_name: Optional[str] = None

class CreateSubject(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: Optional[int] = 1

class CreateLecture(BaseModel):
    subject_code: str
    topic: str
    scheduled_at: Optional[datetime] = None

class CreateExam(BaseModel):
    title: str
    subject_code: str
    scheduled_at: Optional[datetime] = None
    total_marks: int = 100

class CreateGrade(BaseModel):
    roll_number: str
    subject_code: str
    marks_obtained: float
    exam_title: Optional[str] = None
    remarks: Optional[str] = None

# Marketing/Newsletter

class NewsletterSubscriber(BaseModel):
    email: EmailStr
    status: str = Field("pending", description="pending or confirmed")
    token: Optional[str] = None
    confirmed_at: Optional[datetime] = None

class CreateNewsletterSubscribe(BaseModel):
    email: EmailStr
