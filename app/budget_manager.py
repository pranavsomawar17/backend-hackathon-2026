from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import Expense, BudgetAlert


# -----------------------------
# CHANGE BUDGETS ONLY HERE
# -----------------------------
BUDGETS = {

    "Travel": 10000,

    "Software": 100000,

    "Office": 10000,

    "Meals": 10000,

    "Other": 100000

}


def initialize_budgets(db: Session):

    for category, amount in BUDGETS.items():

        existing = db.query(
            BudgetAlert
        ).filter(
            BudgetAlert.department == category
        ).first()

        if existing:

            # Sync if changed in code
            existing.budget = amount

        else:

            new_budget = BudgetAlert(

                department=category,

                budget=amount,

                spent=0,

                alert="Within budget",

                created_at=datetime.utcnow()

            )

            db.add(new_budget)

    db.commit()


def check_budget(category: str, db: Session):

    total_spent = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.category == category
    ).scalar() or 0

    budget_row = db.query(
        BudgetAlert
    ).filter(
        BudgetAlert.department == category
    ).first()

    if not budget_row:
        return

    budget_row.spent = total_spent

    if total_spent > budget_row.budget:

        budget_row.alert = "Budget exceeded"

    else:

        budget_row.alert = "Within budget"

    db.commit()


def check_all_budgets(db: Session):

    for category in BUDGETS.keys():

        check_budget(category, db)