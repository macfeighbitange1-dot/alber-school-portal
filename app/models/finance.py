import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

# IMPORTANT: We import the 'db' from the app, NOT create a new one here
from app import db 

class Student(db.Model):
    __tablename__ = 'students'

    # Note: Using String/TEXT for ID to ensure compatibility with SQLite
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cbc_grade: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    admission_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    fees: Mapped[List["FeeTransaction"]] = relationship(back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.full_name} - Grade {self.cbc_grade}>"

class FeeTransaction(db.Model):
    __tablename__ = 'fee_transactions'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    
    mpesa_receipt_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="fees")

    def __repr__(self):
        return f"<Transaction {self.mpesa_receipt_number} - {self.status}>"