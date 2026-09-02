from fastapi import Body, FastAPI, Path, Query, status, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

expenses_db = {
    1: {"id": 1, "description": "Lunch", "amount": 12.5},
    2: {"id": 2, "description": "Bus ticket", "amount": 2.0},
    3: {"id": 3, "description": "Notebook", "amount": 5.75},
}


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(expense: str = Body(...), amount: float = Body(...)):
    new_id = max(expenses_db.keys(), default=0) + 1

    expense_obj = {"id": new_id, "description": expense, "amount": amount}
    expenses_db[new_id] = expense_obj
    return expense_obj


@app.get("/expenses")
def retrieve_expense_list(
    search: str | None = Query(
        description="it will be searched with the expense you provided",
        example="Rent",
        default=None,
        max_length=50,
    )
):

    if search:
        return [
            item for item in expenses_db.values() if item.get("description") == search
        ]  # [operation iteration condition]

    return expenses_db


@app.get("/expenses/{expense_id}")
def retrieve_expense(
    expense_id: int = Path(
        title="expense id",
        description="the ID of the expense in expenses_db",
    )
):
    if expense_id in expenses_db:
        return expenses_db[expense_id]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
    )


@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(
    expense_id: int, expense: str = Body(...), amount: float = Body(...)
):
    if expense_id in expenses_db:
        expenses_db[expense_id].update({"description": expense, "amount": amount})
        return expenses_db[expense_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
    )


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    if expense_id in expenses_db:
        expenses_db.pop(expense_id)

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
