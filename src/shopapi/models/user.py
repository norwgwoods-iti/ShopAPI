from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shopapi.db.base import Base
from shopapi.models.enums import UserRole


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        nullable=False,
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    cart_items: Mapped[list["CartModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    ) ###

    # orders: Mapped[list["OrderModel"]] = relationship(back_populates="user", cascade="all, delete-orphan") ###