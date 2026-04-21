import time
import asyncpg
import asyncio
from src.services.cach_service import cache_async
from src.database.models import Orders
from src.services.timer_service import Timer
from src.database.connection import async_session_maker
from sqlalchemy import select, update
from src.services.log_service import LogService
from src.database.connection import get_pool
from fastapi import Depends
from typing import List
from src.models.order import  OrderCalculatorAsync

class ProductRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @cache_async()
    async def get_by_id(self, product_id: int) -> dict | None:
        """Получить товар по id"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, price FROM products WHERE id = $1", product_id)
        if row:
            row = dict(row)
            row["price"] = str(row["price"])
            return row
        print("Товар не найден")
        return None

    async def list_products(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Список товаров с пагинацией"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, price FROM products ORDER BY id ASC "
                "LIMIT $1 OFFSET $2", limit, offset)
        if rows:
            return rows
        print("Товар не найден")
        return None

    async def create(self, name: str, price: float, quantity: int) -> int:
        """Создать товар, вернуть id"""
        async with self.pool.acquire() as conn:
            product_id = await conn.fetchval(
                "INSERT INTO products (name, price, quantity) "
                "VALUES ($1, $2, $3) RETURNING id",
                 name, price, quantity)
        if product_id:
            return product_id
        print("Не удалось внести товар")
        return None

    async def update_price(self, product_id: int, new_price: float) -> bool:
        """Обновить цену товара"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE products SET price = $1 WHERE id = $2",
                new_price, product_id)

    async def delete(self, product_id: int) -> bool:
        async with self.pool.acquire() as conn:
            deleted = await conn.execute("DELETE FROM products WHERE id = $1"
                               , product_id)

        return deleted == "DELETE 1"

class OrdersRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_order_from_db(self, order_id: int):
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("SELECT * FROM orders WHERE id = $1", order_id)
        return result

    async def create_order(self, user_id: int, items_list: List[dict]):
        """Создать товар, вернуть id"""
        total = await OrderCalculatorAsync().calculate_total(items_list)
        async with self.pool.acquire() as conn:
            try:
                order_id = await conn.fetchval(
                    "INSERT INTO orders (user_id, total) "
                    "VALUES ($1, $2) RETURNING id",
                     user_id, total)

                for item in items_list:
                    await conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) "
                    "VALUES ($1, $2, $3) RETURNING id",
                     order_id, item.product_id, total)
            except Exception as e:
                log_data = {"id": order_id, "status": str(e)}
                print(log_data)
                return None

async def get_orders_repository(pool=Depends(get_pool)) -> OrdersRepository:
    return OrdersRepository(pool)

async def process_order(order_id: int):
    """Асинхронная обработка одного заказа"""
    try:
        await asyncio.sleep(0.1)
        async with async_session_maker() as session:
            await session.execute(
                update(Orders).where(Orders.id == order_id).values(status="Done")
            )
            await session.commit()


        return f"Заказ {order_id} обработан"
    except Exception as e:
        log_data = {"id": order_id, "status": str(e)}
        # LogService.save_log(log_data)
        print(log_data)
        return None

async def process_orders_async(order_ids: list):
    """Параллельная обработка списка заказов"""
    tasks = [process_order(order_id) for order_id in order_ids]
    results = await asyncio.gather(*tasks)
    return list(results)


async def create_user_in_db(conn, name: str, password: str, email: str, balance: float = 0):
    return await conn.execute(
        "INSERT INTO users (name, password, email, balance) VALUES ($1, $2, $3, $4)",
        name, password, email, balance
    )

async def read_user_in_db(conn, name: str):
    result = await conn.fetchrow("SELECT * FROM users WHERE name = $1", name)
    return dict(result)

# Измерение производительности
async def main():
    order_ids = list(range(101, 103))  # 100 заказов
    with Timer() as timer:
        results = await process_orders_async(order_ids)
    print(results)
    print(type(results))
    print(f"Асинхронная обработка: {timer.result} секунд")




    print(f"Синхронная обработка: {timer.result} секунд")


if __name__ == "__main__":
    asyncio.run(main())


# async def main():
#     pool = await asyncpg.create_pool(**DB_CONFIG,
#                                      min_size=10,
#                                      max_size=20,
#                                      command_timeout=30)
#     products = ProductRepository(pool)
#     result = await products.get_by_id(100)
#     result = await products.get_by_id(100)
#     result = await products.get_by_id(100)
#     # result = await products.list_products(limit=10, offset=0)
#     print(result)
#     # print(type(result))
#     # print(await products.create("Арбуз", 54, 20))
#     # await products.update_price(1003, 100)
#     # print(await products.delete(1003))
#
# if __name__ == "__main__":
#     asyncio.run(main())