from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint

from shopapi.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CartModel(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        CheckConstraint("quantity > 0", name="uq_cart_user_quantity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates='cart_items') ###
    product: Mapped["ProductModel"] = relationship(back_populates='cart_items') ###