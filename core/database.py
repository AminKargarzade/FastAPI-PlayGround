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
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # only for sqlite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# create base class for declaring tables
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30))
    email = Column(String())
    hashed_password = Column(String())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_date = Column(DateTime(), default=datetime.now)
    updated_date = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    expenses = relationship("Expense", backref="user")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, is_active={self.is_active}, is_verified={self.is_verified})"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    description = Column(Text())
    amount = Column(Numeric(10, 2))
    is_paid = Column(Boolean, default=False)
    created_date = Column(DateTime(), default=datetime.now)
    updated_date = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"Expense(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, is_paid={self.is_paid})"
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
