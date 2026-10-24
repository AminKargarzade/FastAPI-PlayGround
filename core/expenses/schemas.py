from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer
from typing import Optional
from datetime import datetime


class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ..., description="Enter Expense Description", min_length=1, max_length=500
    )

    amount: float = Field(..., description="Enter Expense Amount", gt=0)
    is_paid: bool = Field(..., description="Indicates if the expense is paid")

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Description cannot be empty or whitespace")

        return value

    @field_serializer("amount")
    def serialize_amount(self, value: float) -> float:
        return round(value, 2)


class ExpenseCreateSchema(BaseExpenseSchema):
    pass


class ExpenseResponseSchema(BaseExpenseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Unique identifier for the expense")
    user_id: int

    created_date: datetime = Field(
        ..., description="The timestamp when the expense was created"
    )
    updated_date: datetime = Field(
        ..., description="The timestamp when the expense was last updated"
    )


class ExpenseUpdateSchema(BaseModel):
    description: str | None = Field(default=None, max_length=500, min_length=1)

    amount: float | None = Field(default=None, gt=0)

    is_paid: bool | None = Field(
        default=None, description="Indicates if the expense is paid"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Description cannot be empty or whitespace")

        return value
