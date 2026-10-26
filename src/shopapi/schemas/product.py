from datetime import date
from decimal import Decimal

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field


class ProductModel(Base):
    __tablename__ = "products"

    __table_args__ = {
        CheckConstraint("price > 0", name="product_price_check"),
        CheckConstraint("stock >= 0", name="product_stock_check"),
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False) # numeric > 0
    stock: Mapped[int] = mapped_column(nullable=False) # !< 0
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    category: Mapped["CategoryModel"] = relationship(back_populates="products")
    cart_items: Mapped[list["CartModel"]] = relationship(back_populates="products", cascade="all, delete-orphan")
    order_item: Mapped[list["OrderItemModel"]] = relationship(back_populates="products", cascade="all, delete-orphan")


class ProductAddSchema(BaseModel):
    name: str = Field()
    description: str = Field()
    price: Decimal = Field()
    stock: int = Field()

class ProductSchema(ProductAddSchema):
    id: int = Field()
    category_id: int = Field()
    is_active: bool = Field()
    created_at: date = Field()
