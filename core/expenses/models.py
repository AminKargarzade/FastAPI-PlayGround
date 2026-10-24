from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    Numeric,
    Text,
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)
from core.database import Base
from sqlalchemy.orm import relationship


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    description = Column(Text(500), nullable=True)
    amount = Column(Numeric(10, 2))
    is_paid = Column(Boolean, default=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("UserModel", back_populates="expenses", userlist=False)
