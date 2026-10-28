from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shopapi.db.base import Base
from sqlalchemy.sql.sqltypes import Date
from datetime import date, datetime


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default='user') # enum
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    cart_items: Mapped[list["CartModel"]] = relationship(back_populates="user", cascade="all, delete-orphan") ###

    # orders: Mapped[list["OrderModel"]] = relationship(back_populates="user", cascade="all, delete-orphan") ###