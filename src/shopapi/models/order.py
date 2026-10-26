from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.sql.sqltypes import Date

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shopapi.db.base import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(nullable=False) # enum
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # numeric
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="order_items")
    order_item: Mapped[list["OrderItemModel"]] = relationship(back_populates="orders", cascade="all, delete-orphan")

