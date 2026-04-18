from src.database.connection import session_maker, repeatable_read_session_maker
from src.database.models import Orders, Products, Users, OrderItems
from sqlalchemy.orm import selectinload
from src.services.log_service import LogService
import traceback

logging = LogService()

def get_user_orders(user_id):
    with session_maker() as session:
        try:
            user = session.query(Users).options(selectinload(Users.orders)).filter(Users.id == user_id).first()
            if user:
                return [{
                    "id": order.id,
                    "total": order.total,
                    "created_at": order.created_at,
                } for order in user.orders]
            return []
        except Exception as e:
            print(e)

def create_order(user_id, product_id, quantity, total):
    with repeatable_read_session_maker() as session:
        try:
            user = session.query(Users).filter(Users.id == user_id).first()
            product = session.query(Products).filter(Products.id == product_id).first()
            if not user:
                raise ValueError("Пользователь не найден")
            if not product:
                raise ValueError("Продукт не найден")
            if product.quantity < quantity:
                raise ValueError("Недостаточно товара на складе")
            if user.balance < total:
                raise ValueError("Недостаточно средств")
            user.balance -= total
            product.quantity -= quantity
            order = Orders(user_id=user_id, total=total)
            order_items = OrderItems(product_id=product.id, quantity=quantity)
            order.items.append(order_items)
            session.add(order)
            session.commit()
        except ValueError as e:
            session.rollback()
            print(e)

def read_user(user_id):
    with session_maker() as session:
        try:
            user = session.query(Users).filter(Users.id == user_id).first()
            if user is None:
                raise ValueError("Пользователь не найден")
            return user
        except ValueError as e:
            stack_trace = traceback.format_exc()
            log_data = {"type": "error", "stack_trace": stack_trace, "status_code": 404}
            logging.save_log(log_data)
            return e


def get_product_from_db(product_id):
    with session_maker() as session:

        product = session.query(Products).filter(Products.id == product_id).first()
        if product:
            return product
        else:
            raise ValueError("Товар не найден")


def get_all_products_from_db():
    with session_maker() as session:
        try:
            products = session.query(Products).all()
            return products
        except ValueError as e:
            return e

if __name__ == "__main__":
    # create_order(25, 1002, 2, 4000)
    print(get_product_from_db(1))
    # user = get_user_orders(30)
    # for order in user:
    #     print(order)