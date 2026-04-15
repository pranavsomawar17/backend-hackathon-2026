from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.models import Expense, BudgetAlert
from app.llm import categorize_expense
from app.budget_manager import (
    initialize_budgets,
    check_budget
)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Request Models
# ---------------------------

class ExpenseRequest(BaseModel):

    description: str
    amount: float
    employee_id: str


class BudgetRequest(BaseModel):

    category: str
    amount: float


# ---------------------------
# Startup
# ---------------------------

@app.on_event("startup")
def startup():

    db = SessionLocal()

    initialize_budgets(db)

    db.close()


# ---------------------------
# Root
# ---------------------------

@app.get("/")
def home():

    return {
        "message": "ExpenseIQ API running"
    }


# ---------------------------
# Create Expense
# ---------------------------

@app.post("/expenses")
def create_expense(data: ExpenseRequest):

    db = SessionLocal()

    category = categorize_expense(
        data.description
    )

    expense = Expense(

        description=data.description,

        amount=data.amount,

        employee_id=data.employee_id,

        category=category
    )

    db.add(expense)

    db.commit()

    check_budget(category, db)

    db.close()

    return {

        "category": category,

        "amount": int(data.amount)

    }


# ---------------------------
# Get All Expenses
# ---------------------------

@app.get("/expenses")
def get_all_expenses():

    db = SessionLocal()

    expenses = db.query(
        Expense
    ).order_by(
        Expense.created_at.desc()
    ).limit(50).all()

    result = []

    for e in expenses:

        result.append({

            "description": e.description,

            "amount": int(e.amount),

            "category": e.category,

            "employee_id": e.employee_id

        })

    db.close()

    return result


# ---------------------------
# Summary by Category
# ---------------------------

@app.get("/expenses/summary")
def get_summary():

    db = SessionLocal()

    results = db.query(

        Expense.category,

        func.sum(Expense.amount)

    ).group_by(

        Expense.category

    ).all()

    db.close()

    return {

        r[0]: int(r[1])

        for r in results

    }


# ---------------------------
# Analytics (KPI + Bar Chart)
# ---------------------------

@app.get("/expenses/analytics")
def analytics():

    db = SessionLocal()

    total = db.query(
        func.sum(Expense.amount)
    ).scalar() or 0

    count = db.query(
        func.count(Expense.id)
    ).scalar() or 0

    max_expense = db.query(
        func.max(Expense.amount)
    ).scalar() or 0

    average = 0

    if count > 0:

        average = total / count

    db.close()

    return {

        "total_expense": int(total),

        "average_expense": int(average),

        "max_expense": int(max_expense),

        "transaction_count": int(count)

    }


# ---------------------------
# Employee Expenses
# ---------------------------

@app.get("/expenses/employee/{employee_id}")
def employee_expenses(employee_id: str):

    db = SessionLocal()

    expenses = db.query(
        Expense
    ).filter(
        Expense.employee_id == employee_id
    ).all()

    result = []

    for e in expenses:

        result.append({

            "description": e.description,

            "amount": int(e.amount),

            "category": e.category,

            "employee_id": e.employee_id

        })

    db.close()

    return result


# ---------------------------
# Set Budget
# ---------------------------

@app.post("/budget/set")
def set_budget(data: BudgetRequest):

    db = SessionLocal()

    budget = db.query(
        BudgetAlert
    ).filter(
        BudgetAlert.department == data.category
    ).first()

    if budget:

        budget.budget = data.amount

    else:

        budget = BudgetAlert(

            department=data.category,

            budget=data.amount,

            spent=0,

            alert="Within budget"

        )

        db.add(budget)

    db.commit()

    db.close()

    return {

        "status": "ok"

    }


# ---------------------------
# Get Budgets
# ---------------------------

@app.get("/budgets")
def get_budgets():

    db = SessionLocal()

    budgets = db.query(
        BudgetAlert
    ).all()

    result = []

    for b in budgets:

        result.append({

            "category": b.department,

            "budget": int(b.budget),

            "spent": int(b.spent),

            "alert": b.alert

        })

    db.close()

    return result