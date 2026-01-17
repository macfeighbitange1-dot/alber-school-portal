from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from pydantic import BaseModel, Field, EmailStr

db = SQLAlchemy()

# --- Database Entity ---
class Student(db.Model):
    __tablename__ = 'students'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    admission_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    grade_level: Mapped[int] = mapped_column(nullable=False) # 1-9
    parent_phone: Mapped[str] = mapped_column(nullable=False) # For M-Pesa
    
    # Relationships (to be defined in fee.py/cbc_strand.py)
    # fees = relationship("FeeRecord", back_populates="student")

# --- Pydantic Validator (Service Layer) ---
class StudentAdmissionSchema(BaseModel):
    full_name: str = Field(..., min_length=3)
    grade_level: int = Field(..., ge=1, le=9, description="CBC Grade 1-9")
    parent_phone: str = Field(..., pattern=r"^2547\d{8}$", description="Format: 2547XXXXXXXX")
    parent_email: EmailStr | None = None