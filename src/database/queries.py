from datetime import date, timedelta
from dataclasses import dataclass
import random
from time import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE, ISOLATION_LEVEL_READ_COMMITTED
from src.database.connection import get_connection

def create_order(user_id, product_id, quantity, total):
    """Создание заказа с атомарными операциями"""

    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (user_id, total) VALUES (%s, %s)",
                    (user_id, total)
                )
                cur.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                    (quantity, product_id)
                )
                cur.execute(
                    "UPDATE users SET balance = balance - %s WHERE id = %s",
                    (total, user_id)
                )

                cur.execute("SELECT quantity FROM products WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно товара на складе")

                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно средств")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

        except ValueError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            raise

def transfer_money(from_user_id, to_user_id, amount):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s",
                            (amount, from_user_id))

                cur.execute("SELECT balance FROM users WHERE id = %s", (from_user_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно средств")

                cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s",
                            (amount, to_user_id))

                conn.commit()
                return True

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

        except ValueError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            raise

def generate_sales_report(start_date):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT SUM(total) FROM orders WHERE created_at >= %s", (start_date,))
                total = cur.fetchone()[0] or 0
                cur.execute("SELECT COUNT(*) FROM orders WHERE created_at >= %s", (start_date,))
                count = cur.fetchone()[0] or 0
                return {"total": total, "count": count}

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

def read_user_balance(user_id):
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        try:
            with conn.cursor() as cur:

                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                balance = cur.fetchone()
                if balance is not None:
                    return {"user_id": user_id,"balance": balance[0]}
                raise ValueError

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

        except ValueError:
            conn.rollback()
            print(f"Пользователь не найден")
            raise

def calculate_total_revenue():
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT SUM(total) FROM orders")
                total = cur.fetchone()[0] or 0
                conn.commit()
                return {"total": total}

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

def create_order_with_acid(user_id, product_id, quantity, total):
    """Создание заказа с атомарными операциями"""
    with get_connection() as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
                result = cur.fetchone()
                if result[0] < quantity:
                    raise ValueError("Недостаточно товара на складе")

                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result[0] < total:
                    raise ValueError("Недостаточно средств")

                cur.execute(
                    "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id",
                    (user_id, total)
                )
                order_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, product_id, quantity)
                )
                cur.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                    (quantity, product_id)
                )
                cur.execute(
                    "UPDATE users SET balance = balance - %s WHERE id = %s",
                    (total, user_id)
                )

                cur.execute("SELECT quantity FROM products WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно товара на складе")

                cur.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result[0] < 0:
                    raise ValueError("Недостаточно средств")

                conn.commit()
                return True

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

        except ValueError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            raise

class Timer:
    def __init__(self):
        self.result = None

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time()
        self.result = end_time - self.start_time

@dataclass
class IndexData:
    table_name: str
    field_name: str

    def __post_init__(self):
        self.index = f"idx_{self.table_name}_{self.field_name}"

def _measure_index_performance(index_data: IndexData, search_param):
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                timer = Timer()
                measurements = {}
                query = ("SELECT {field} FROM {table} WHERE {field} = %s".format(
                    field=index_data.field_name,
                    table=index_data.table_name
                ))
                index_query = f"DROP INDEX IF EXISTS {index_data.index}"
                cur.execute(index_query)
                with timer as timer:
                    cur.execute(query, (search_param,))
                    _ = cur.fetchone()
                time_without_index = timer.result
                measurements["without_index"] = round(time_without_index, 5)
                index_query = f"CREATE INDEX {index_data.index} ON {index_data.table_name}({index_data.field_name})"
                cur.execute(index_query)
                with timer as timer:
                    cur.execute(query, (search_param,))
                    _ = cur.fetchone()
                time_with_index = timer.result
                measurements["with_index"] = round(time_with_index, 5)
                measurements["index_diff"] = round(time_without_index - time_with_index, 6)

                result_str = (f"Запрос {query}:\n"
                              f"Без индекса: {measurements['without_index']} сек\n"
                              f"С индексом: {measurements['with_index']} сек\n"
                              f"Ускорение: {measurements['index_diff']} сек")
                return result_str
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Ошибка в БД: {e}")
            raise

        except ValueError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            raise

def get_user_orders_with_products(user_id):
    """Проблема: нет анализа производительности"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT o.id, o.total, p.name, p.price
                    FROM orders o
                    JOIN order_items oi on oi.order_id = o.id
                    JOIN products p ON oi.product_id = p.id
                    WHERE o.user_id = %s
            """, (user_id,))
            return cur.fetchall()

if __name__ == "__main__":
    # transfer_money(2, 1, 5000)
    today = date.today() - timedelta(days=3)
    # print(today)
    # print(calculate_total_revenue())
    # print(read_user_balance("4"))
    # index = IndexData(table_name="users", field_name="email")
    # print(_measure_index_performance(index, "abc@gmail.com"))

    # with get_connection() as conn:
    #     with conn.cursor() as cur:
    #         for i in range(1,1000):
    #             try:
    #                 product_id = random.randint(1, 1000)
    #                 cur.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    #                 price = cur.fetchone()[0]
    #                 quantity = random.randint(1, 2)
    #                 total = quantity * price
    #                 user_id = random.randint(1, 1000)
    #                 create_order_with_acid(user_id=user_id, product_id=product_id, quantity=quantity, total=total)
    #             except ValueError as e:
    #
    #                 print(e)
















