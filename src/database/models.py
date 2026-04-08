from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Numeric, DateTime, String, ForeignKey, text, Integer
from src.database.connection import session_maker

class BaseORM(DeclarativeBase):
    _repr_cols_num = 3
    _repr_cols = tuple()
    def __repr__(self):
        cols = []
        for index, col in enumerate(self.__table__.columns.keys()):
            if col in self._repr_cols or index < self._repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"{self.__class__.__name__}({', '.join(cols)})"


class Orders(BaseORM):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),  nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"),  nullable=False)

    users: Mapped["Users"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItems"]] = relationship(back_populates="orders")

class Users(BaseORM):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    orders: Mapped[List["Orders"]] = relationship(back_populates="users")
    reviews: Mapped[List["Reviews"]] = relationship(back_populates="users")

class Products(BaseORM):
    __tablename__ = "products"
    _repr_cols = ("quantity")

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    items: Mapped[List["OrderItems"]] = relationship(back_populates="product")
    reviews: Mapped[List["Reviews"]] = relationship(back_populates="product")

class OrderItems(BaseORM):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()

    product : Mapped["Products"] = relationship(back_populates="items")
    orders: Mapped["Orders"] = relationship(back_populates="items")

class Reviews(BaseORM):
    __tablename__ = "reviews"
    _repr_cols = ("rating")

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(nullable=False)
    review_text: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    users: Mapped["Users"] = relationship(back_populates="reviews")
    product: Mapped["Products"] = relationship(back_populates="reviews")

if __name__ == "__main__":
    with session_maker() as session:
        order = session.query(Orders).filter(Orders.id == 1).first()
        user = session.query(Users).filter(Users.id == 1).first()
        products = session.query(Products).filter(Products.id == 1).first()
        order_items = session.query(OrderItems).filter(OrderItems.id == 1).first()
        reviews = session.query(Reviews).filter(Reviews.id == 1).first()
        print(order)
        print(user)
        print(products)
        print(order_items)
        print(reviews)
        print(reviews.product)
