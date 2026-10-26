class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default='user') # enum
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    cart_items: Mapped[list["CartModel"]] = relationship(back_populates="users", cascade="all, delete-orphan")
    orders: Mapped[list["ProductModel"]] = relationship(back_populates="users", cascade="all, delete-orphan")



