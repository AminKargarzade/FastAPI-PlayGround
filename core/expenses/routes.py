from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from auth.jwt_cookie_auth import get_authenticated_user
from users.models import UserModel
from expenses.models import ExpenseModel
from expenses.schemas import (
    ExpenseCreateSchema,
    ExpenseResponseSchema,
    ExpenseUpdateSchema,
)
from i18n.dependencies import get_language
from gettext import NullTranslations

router = APIRouter(tags=["Expenses"])


@router.post(
    "/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseResponseSchema,
)
def create_expense(
    request: ExpenseCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user),
):
    new_expense = ExpenseModel(
        user_id=current_user.id,
        description=request.description,
        amount=request.amount,
        is_paid=request.is_paid,
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


@router.get(
    "/expenses",
    response_model=list[ExpenseResponseSchema],
)
def retrieve_expense_list(
    search: str | None = Query(
        default=None,
        description="Search expenses by description",
        max_length=50,
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user),
):
    query = db.query(ExpenseModel).filter(ExpenseModel.user_id == current_user.id)

    if search:
        query = query.filter(ExpenseModel.description.contains(search))

    return query.all()


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponseSchema,
)
def retrieve_expense(
    expense_id: int = Path(..., title="Expense ID", gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user),
    translator: NullTranslations = Depends(get_language),
):
    expense = (
        db.query(ExpenseModel)
        .filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.user_id == current_user.id,
        )
        .one_or_none()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translator.gettext("Expense not found"),
        )

    return expense


@router.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponseSchema,
)
def update_expense_detail(
    request: ExpenseUpdateSchema,
    expense_id: int = Path(..., title="Expense ID", gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user),
    translator: NullTranslations = Depends(get_language),
):
    expense = (
        db.query(ExpenseModel)
        .filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.user_id == current_user.id,
        )
        .one_or_none()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translator.gettext("Expense not found"),
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


@router.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_200_OK,
)
def delete_expense(
    expense_id: int = Path(..., title="Expense ID", gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_authenticated_user),
    translator: NullTranslations = Depends(get_language),
):
    expense = (
        db.query(ExpenseModel)
        .filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.user_id == current_user.id,
        )
        .one_or_none()
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    db.delete(expense)
    db.commit()

    return {"message": translator.gettext("Expense deleted successfully")}
