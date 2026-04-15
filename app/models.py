from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String)

    description = Column(String)

    amount = Column(Float)

    category = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class BudgetAlert(Base):

    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True)

    department = Column(String)

    budget = Column(Float)

    spent = Column(Float)

    alert = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )