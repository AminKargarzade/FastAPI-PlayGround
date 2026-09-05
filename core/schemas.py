from pydantic import BaseModel, Field, field_validator, field_serializer


class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ..., description="Enter Expense Description", min_length=1, max_length=50
    )

    amount: float = Field(..., description="Enter Expense Amount", gt=0)

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
    id: int = Field(..., description="Unique identifier for the expense")


class ExpenseUpdateSchema(BaseModel):
    description: str | None = Field(default=None, max_length=50)

    amount: float | None = Field(default=None, gt=0)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Description cannot be empty or whitespace")

        return value
