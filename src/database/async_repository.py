import asyncpg
import asyncio
from src.database.connection import DB_CONFIG
from src.services.cach_service import cache_async

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

async def main():
    pool = await asyncpg.create_pool(**DB_CONFIG,
                                     min_size=10,
                                     max_size=20,
                                     command_timeout=30)
    products = ProductRepository(pool)
    result = await products.get_by_id(100)
    result = await products.get_by_id(100)
    result = await products.get_by_id(100)
    # result = await products.list_products(limit=10, offset=0)
    print(result)
    # print(type(result))
    # print(await products.create("Арбуз", 54, 20))
    # await products.update_price(1003, 100)
    # print(await products.delete(1003))

if __name__ == "__main__":
    asyncio.run(main())