from fastapi import Body, FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
import random

app = FastAPI()

expenses_db = [
    {"id": 1, "description": "Lunch", "amount": 12.5},
    {"id": 2, "description": "Bus ticket", "amount": 2.0},
    {"id": 3, "description": "Notebook", "amount": 5.75},
]


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(expense: str = Body(...), amount: float = Body(...)):
    expense_obj = {"id": random.randint(1, 1000), "description": expense, "amount": amount}  # type: ignore
    expenses_db.append(expense_obj)  # type: ignore
    return expense_obj


@app.get("/")
async def read_root():
    return {"Hello": "World"}
