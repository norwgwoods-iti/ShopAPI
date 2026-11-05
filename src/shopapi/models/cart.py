from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint

from shopapi.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CartModel(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        CheckConstraint("quantity > 0", name="ck_cart_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete="RESTRICT"), # RESTRICT не позводит удалить товар, если он в чей-то корзине
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
    )

    user: Mapped["UserModel"] = relationship(
        back_populates='cart_items'
    )
    product: Mapped["ProductModel"] = relationship(
        back_populates='cart_items'
    )