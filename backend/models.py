from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    HR = "hr"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.STAFF)
    department = Column(String(100))
    designation = Column(String(100))
    phone = Column(String(15))
    bank_account = Column(String(50))
    bank_name = Column(String(100))
    ifsc_code = Column(String(20))
    pan_number = Column(String(20))
    joining_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    salary_structure = relationship("SalaryStructure", back_populates="user", uselist=False)
    payrolls = relationship("Payroll", foreign_keys="Payroll.user_id", back_populates="user")

class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    basic_salary = Column(Float)
    hra = Column(Float, default=0)
    ta = Column(Float, default=0)
    medical_allowance = Column(Float, default=0)
    special_allowance = Column(Float, default=0)
    pf_deduction = Column(Float, default=0)
    tax_deduction = Column(Float, default=0)
    other_deductions = Column(Float, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="salary_structure")

class Payroll(Base):
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(Integer)
    year = Column(Integer)
    basic_salary = Column(Float)
    total_allowances = Column(Float)
    total_deductions = Column(Float)
    gross_salary = Column(Float)
    net_salary = Column(Float)
    working_days = Column(Integer, default=30)
    present_days = Column(Integer, default=30)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime, nullable=True)
    remarks = Column(String(500))
    generated_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="payrolls")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    status = Column(String(20))
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id])

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    leave_type = Column(String(50))
    from_date = Column(DateTime)
    to_date = Column(DateTime)
    days_count = Column(Integer)
    reason = Column(String(500))
    status = Column(String(20), default="pending")
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id])
