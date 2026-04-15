from pydantic import BaseModel

class ExpenseCreate(BaseModel):

    description: str

    amount: float

    employee_id: str