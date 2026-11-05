from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from shopapi.db.base import Base
from sqlalchemy import String, ForeignKey, Text, CheckConstraint, Numeric, DateTime, func



class ProductModel(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint("price > 0", name="product_price_check"),
        CheckConstraint("stock >= 0", name="product_stock_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='RESTRICT'),  # !!!! ondelete
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    ) # numeric > 0
    stock: Mapped[int] = mapped_column(nullable=False) # !< 0
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


    category: Mapped["CategoryModel"] = relationship(
        back_populates="products"
    ) ###
    cart_items: Mapped[list["CartModel"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    ) ###
    # order_items: Mapped[list["OrderItemModel"]] = relationship(
    #     back_populates="product",
    # ) ###