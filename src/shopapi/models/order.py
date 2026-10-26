from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, DateTime
from sqlalchemy.sql.sqltypes import Date

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shopapi.db.base import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(nullable=False) # enum
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # numeric
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="orders") ###
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="order") ### cascade?!

