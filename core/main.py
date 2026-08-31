from fastapi import Body, FastAPI, Path, Query, status, HTTPException
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


@app.get("/expenses")
def retrieve_expense_list(
    q: str | None = Query(
        alias="search",
        description="it will be searched with the expense you provided",
        example="Rent",
        default=None,
        max_length=50,
    )
):

    if q:
        return [
            item for item in expenses_db if item["description"] == q
        ]  # [operation iteration condition]
    return expenses_db


@app.get("/expenses/{expense_id}")
def retrieve_expense(
    expense_id: int = Path(
        alias="expense_id",
        title="expense id",
        description="the ID of the expense in expenses_db",
    )
):
    for expense in expenses_db:
        if expense["id"] == expense_id:
            return expense
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
    )


@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(
    expense_id: int, expense: str = Body(...), amount: float = Body(...)
):
    for exp in expenses_db:
        if exp["id"] == expense_id:
            exp["description"] = expense
            exp["amount"] = amount
            return exp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
    )


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for exp in expenses_db:
        if exp["id"] == expense_id:
            expenses_db.remove(exp)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Expense deleted successfully"},
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
    )


@app.get("/")
async def read_root():
    return {"Hello": "World"}
