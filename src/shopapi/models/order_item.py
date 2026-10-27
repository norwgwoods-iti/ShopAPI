from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

from shopapi.db.base import Base
from sqlalchemy import ForeignKey, CheckConstraint, Numeric


class OrderItemModel(Base):
    __tablename__ = 'order_items'

    __table_args__ = (
        CheckConstraint("quantity > 0", name="order_item_quantity"),
        CheckConstraint("unit_price > 0", name="order_item_quantity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(nullable=False, server_default='1') # > 0
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default='1') # numeric > 0

    order: Mapped["OrderModel"] = relationship(back_populates="order_items") ###
    product: Mapped["ProductModel"] = relationship(back_populates="order_items") ###

