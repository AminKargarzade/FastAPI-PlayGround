from fastapi import Depends, FastAPI, Path, Query, status, HTTPException
from fastapi.responses import JSONResponse
from database import get_db, Expense, SessionLocal, User
from sqlalchemy.orm import Session
from schemas import ExpenseCreateSchema, ExpenseResponseSchema, ExpenseUpdateSchema

app = FastAPI()

@app.on_event("startup")
def create_test_user():
    db = SessionLocal()

    user = db.query(User).filter(User.id == 1).first()

    if not user:
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="test-password",
        )
        db.add(user)
        db.commit()

    db.close()



@app.post(
    "/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseResponseSchema,
)
def create_expense(request: ExpenseCreateSchema, db: Session = Depends(get_db)):
    new_expense = Expense(user_id=request.user_id, description=request.description, amount=request.amount)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense


@app.get("/expenses", response_model=list[ExpenseResponseSchema])
def retrieve_expense_list(
    search: str | None = Query(
        description="it will be searched with the expense you provided",
        example="Rent",
        default=None,
        max_length=50,
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Expense)
    
    if search:
        query = query.filter_by(description=search)
    result = query.all()
    return result


@app.get("/expenses/{expense_id}", response_model=ExpenseResponseSchema)
def retrieve_expense(
    expense_id: int = Path(
        title="expense id",
        description="the ID of the expense in expenses_db",
    ),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter_by(id=expense_id).one_or_none()
    if expense:
        return expense
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )


@app.put(
    "/expenses/{expense_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExpenseResponseSchema,
)
def update_expense_detail(
    request: ExpenseUpdateSchema,
    expense_id: int = Path(..., title="expense id"),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter_by(id=expense_id).one_or_none()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(expense, field, value)
        
    db.commit()
    db.refresh(expense)
    
    return expense


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter_by(id=expense_id).one_or_none()
    if expense:
        db.delete(expense)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Expense deleted successfully"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )


@app.get("/")
async def read_root():
    return {"Hello": "World"}
