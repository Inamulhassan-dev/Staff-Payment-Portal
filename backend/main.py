from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from pathlib import Path
import models
from database import get_db, engine
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)
from pydantic import BaseModel
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Staff Payment Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    employee_id: str
    email: str
    password: str
    full_name: str
    department: str
    designation: str
    phone: str
    bank_account: str
    bank_name: str
    ifsc_code: str
    pan_number: str

class SalaryStructureCreate(BaseModel):
    user_id: int
    basic_salary: float
    hra: float = 0
    ta: float = 0
    medical_allowance: float = 0
    special_allowance: float = 0
    pf_deduction: float = 0
    tax_deduction: float = 0
    other_deductions: float = 0

class PayrollGenerate(BaseModel):
    month: int
    year: int
    user_ids: List[int]

class LeaveRequestCreate(BaseModel):
    leave_type: str
    from_date: datetime
    to_date: datetime
    days_count: int
    reason: str

class ChatMessage(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "employee_id": user.employee_id
        }
    }

@app.post("/api/admin/users")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    existing_user = db.query(models.User).filter(
        (models.User.email == user_data.email) | 
        (models.User.employee_id == user_data.employee_id)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = models.User(
        **user_data.dict(exclude={'password'}),
        password_hash=get_password_hash(user_data.password),
        role=models.UserRole.STAFF
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.get("/api/admin/users")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    users = db.query(models.User).filter(models.User.is_active == True).all()
    return users

@app.post("/api/admin/salary-structure")
async def create_salary_structure(
    salary_data: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.SalaryStructure).filter(
        models.SalaryStructure.user_id == salary_data.user_id
    ).first()
    
    if existing:
        for key, value in salary_data.dict().items():
            setattr(existing, key, value)
        db.commit()
        return {"message": "Salary structure updated"}
    else:
        new_structure = models.SalaryStructure(**salary_data.dict())
        db.add(new_structure)
        db.commit()
        return {"message": "Salary structure created"}

@app.post("/api/admin/generate-payroll")
async def generate_payroll(
    payroll_data: PayrollGenerate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    generated_count = 0
    
    for user_id in payroll_data.user_ids:
        existing = db.query(models.Payroll).filter(
            models.Payroll.user_id == user_id,
            models.Payroll.month == payroll_data.month,
            models.Payroll.year == payroll_data.year
        ).first()
        
        if existing:
            continue
        
        salary_structure = db.query(models.SalaryStructure).filter(
            models.SalaryStructure.user_id == user_id
        ).first()
        
        if not salary_structure:
            continue
        
        total_allowances = (
            salary_structure.hra +
            salary_structure.ta +
            salary_structure.medical_allowance +
            salary_structure.special_allowance
        )
        
        total_deductions = (
            salary_structure.pf_deduction +
            salary_structure.tax_deduction +
            salary_structure.other_deductions
        )
        
        gross_salary = salary_structure.basic_salary + total_allowances
        net_salary = gross_salary - total_deductions
        
        new_payroll = models.Payroll(
            user_id=user_id,
            month=payroll_data.month,
            year=payroll_data.year,
            basic_salary=salary_structure.basic_salary,
            total_allowances=total_allowances,
            total_deductions=total_deductions,
            gross_salary=gross_salary,
            net_salary=net_salary,
            generated_by=current_user.id,
            status=models.PaymentStatus.PENDING
        )
        
        db.add(new_payroll)
        generated_count += 1
    
    db.commit()
    
    return {"message": f"Generated payroll for {generated_count} employees"}

@app.get("/api/admin/payrolls")
async def get_all_payrolls(
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    query = db.query(models.Payroll)
    
    if month:
        query = query.filter(models.Payroll.month == month)
    if year:
        query = query.filter(models.Payroll.year == year)
    
    payrolls = query.all()
    return payrolls

@app.put("/api/admin/payrolls/{payroll_id}/status")
async def update_payroll_status(
    payroll_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    payroll = db.query(models.Payroll).filter(models.Payroll.id == payroll_id).first()
    
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    payroll.status = models.PaymentStatus(status)
    if status == "paid":
        payroll.payment_date = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Payroll status updated"}

@app.get("/api/staff/profile")
async def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

@app.get("/api/staff/payslips")
async def get_my_payslips(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payslips = db.query(models.Payroll).filter(
        models.Payroll.user_id == current_user.id
    ).order_by(models.Payroll.year.desc(), models.Payroll.month.desc()).all()
    
    return payslips

@app.get("/api/staff/salary-structure")
async def get_my_salary_structure(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    structure = db.query(models.SalaryStructure).filter(
        models.SalaryStructure.user_id == current_user.id
    ).first()
    
    if not structure:
        raise HTTPException(status_code=404, detail="Salary structure not found")
    
    return structure

@app.get("/api/admin/reports/summary")
async def get_payroll_summary(
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    query = db.query(models.Payroll)
    
    if month:
        query = query.filter(models.Payroll.month == month)
    if year:
        query = query.filter(models.Payroll.year == year)
    
    payrolls = query.all()
    
    total_gross = sum(p.net_salary for p in payrolls)
    total_deductions = sum(p.total_deductions for p in payrolls)
    paid_count = len([p for p in payrolls if p.status == models.PaymentStatus.PAID])
    pending_count = len([p for p in payrolls if p.status == models.PaymentStatus.PENDING])
    
    return {
        "total_employees": len(payrolls),
        "total_gross_salary": total_gross,
        "total_deductions": total_deductions,
        "paid_count": paid_count,
        "pending_count": pending_count
    }

@app.get("/api/staff/leaves")
async def get_my_leaves(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.LeaveRequest).filter(
        models.LeaveRequest.user_id == current_user.id
    ).order_by(models.LeaveRequest.created_at.desc()).all()

@app.post("/api/staff/leaves")
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_leave = models.LeaveRequest(
        user_id=current_user.id,
        **leave_data.dict()
    )
    db.add(new_leave)
    db.commit()
    return {"message": "Leave request submitted successfully"}

@app.get("/api/admin/leaves")
async def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    # Retrieve leave requests with user information (employee IDs etc)
    leaves = db.query(models.LeaveRequest).order_by(models.LeaveRequest.created_at.desc()).all()
    result = []
    for leave in leaves:
        user = db.query(models.User).filter(models.User.id == leave.user_id).first()
        leave_dict = {
            "id": leave.id,
            "user_id": leave.user_id,
            "leave_type": leave.leave_type,
            "from_date": leave.from_date,
            "to_date": leave.to_date,
            "days_count": leave.days_count,
            "reason": leave.reason,
            "status": leave.status,
            "created_at": leave.created_at,
            "employee_name": user.full_name if user else "Unknown",
            "employee_id": user.employee_id if user else ""
        }
        result.append(leave_dict)
    return result

@app.put("/api/admin/leaves/{leave_id}/status")
async def update_leave_status(
    leave_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    leave.status = status
    leave.approved_by = current_user.id
    db.commit()
    return {"message": f"Leave request {status}"}

# AI Mock Endpoints
@app.post("/api/staff/ai/chat")
async def staff_ai_chat(
    msg: ChatMessage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    text = msg.message.lower()
    response = "I'm your HR AI Assistant. I can help with general HR questions. How can I assist you today?"
    if "leave balance" in text or "my leaves" in text:
        leaves = db.query(models.LeaveRequest).filter(models.LeaveRequest.user_id == current_user.id, models.LeaveRequest.status == "approved").all()
        used = sum(l.days_count for l in leaves)
        response = f"You have used {used} leave days this year. As per standard policy, staff receive 20 days per year."
    elif "payday" in text or "salary date" in text:
        response = "Salaries are typically disbursed by the 1st of every month."
    elif "tax" in text:
        structure = db.query(models.SalaryStructure).filter(models.SalaryStructure.user_id == current_user.id).first()
        if structure and structure.tax_deduction > 0:
            response = f"Your current monthly tax deduction is Rs.{structure.tax_deduction}. Please contact HR if you need an updated Form 16."
        else:
            response = "You currently have 0 tax deductions registered in your profile."
            
    return {"response": response}

@app.post("/api/admin/ai/chat")
async def admin_ai_chat(
    msg: ChatMessage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    text = msg.message.lower()
    response = "I'm the System Administrator AI. I can securely query the database. Try asking about 'staff count', 'total payroll', or 'pending work'."
    
    if "staff" in text or "employee" in text or "how many" in text:
        count = db.query(models.User).filter(models.User.role == "staff").count()
        response = f"The organization currently has {count} active staff members registered."
    elif "payroll" in text or "cost" in text or "total" in text:
        from sqlalchemy import func
        total = db.query(func.sum(models.Payroll.net_salary)).scalar() or 0
        response = f"The total lifetime payroll dispatched by the organization is Rs.{total:,.2f}."
    elif "pending" in text or "work" in text or "leave" in text:
        leave_count = db.query(models.LeaveRequest).filter(models.LeaveRequest.status == "pending").count()
        pay_count = db.query(models.Payroll).filter(models.Payroll.status == "pending").count()
        
        response = f"You have {leave_count} pending leave requests to approve. There are also {pay_count} pending payrolls."
        
    return {"response": response}

@app.get("/api/admin/ai/predict-payroll")
async def predict_payroll(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    # A simple deterministic forecast algorithm
    payrolls = db.query(models.Payroll).all()
    if not payrolls:
        return {"predicted_cost": 0, "message": "Not enough data to predict."}
    
    # Calculate average gross salary per employee based on latest structures
    structures = db.query(models.SalaryStructure).all()
    projected_cost = 0
    for s in structures:
        projected_cost += (s.basic_salary + s.hra + s.ta + s.medical_allowance + s.special_allowance)
    
    # Add a slight 2% assumed variable drift/overtime factor representing AI predicted variables
    prediction = projected_cost * 1.02
    
    return {
        "predicted_cost": round(prediction, 2),
        "message": f"AI models predict an estimated payroll cost of Rs.{round(prediction, 2):,} for next month based on active staff salaries and historical variances."
    }


@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    admin = db.query(models.User).filter(models.User.email == "admin@staff.com").first()
    
    if not admin:
        admin = models.User(
            employee_id="ADMIN001",
            email="admin@staff.com",
            password_hash=get_password_hash("admin123"),
            full_name="System Administrator",
            role=models.UserRole.ADMIN,
            department="IT",
            designation="Administrator",
            phone="9999999999",
            bank_account="000000000",
            bank_name="SYSTEM",
            ifsc_code="SYS0000",
            pan_number="ADMIN0000A"
        )
        db.add(admin)
        db.commit()
        print("Default admin created: admin@staff.com / admin123")


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
