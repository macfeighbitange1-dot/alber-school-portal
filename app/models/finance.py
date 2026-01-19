import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Import the db from your app factory
from app import db 

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="student") # 'admin' or 'student'
    
    # One-to-One: If this user is a student, they have a student profile
    student_profile: Mapped[Optional["Student"]] = relationship(back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    admission_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    cbc_grade: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_phone: Mapped[str] = mapped_column(String(15), nullable=False)
    
    # Academic Data
    current_report_url: Mapped[Optional[str]] = mapped_column(String(255)) # Link to PDF/Report
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="student_profile")
    fees: Mapped[List["FeeTransaction"]] = relationship(back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.full_name} - {self.admission_no}>"

class FeeTransaction(db.Model):
    __tablename__ = 'fee_transactions'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    
    mpesa_receipt_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="fees")

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str] = mapped_column(String(20), default="student") # Who sees this?
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))