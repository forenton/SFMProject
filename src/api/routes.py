from fastapi import FastAPI, Depends
import asyncio
import asyncpg
import httpx
from contextlib import asynccontextmanager
from src.database.connection import DB_CONFIG
from src.services.cach_service import async_redis_client
from src.database.async_repository import process_orders_async as process_orders
from pydantic import BaseModel
from typing import List

class OrderProcessModel(BaseModel):
    order_list: List[int]

db_pool: asyncpg.Pool | None = None
http_client: httpx.AsyncClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global db_pool, http_client
    # Создание пула при старте
    db_pool = await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=5,
        max_size=20
    )

    http_client = httpx.AsyncClient(timeout=5.0)
    yield

    # Закрытие пула при остановке
    await db_pool.close()
    await http_client.aclose()
    print("Connection pool закрыт")

app = FastAPI(lifespan=lifespan)

async def get_db():
    """Dependency для получения соединения из пула"""
    async with db_pool.acquire() as conn:
        yield conn

@app.get("/api/products/{product_id}/full")
async def get_product_full(product_id: int, conn=Depends(get_db)):
    """Полная информация о товаре из трёх источников"""
    async def get_product(product_id: int):
        product = await conn.fetchrow(
            "SELECT id, name, price, quantity FROM products WHERE id = $1",
            product_id
        )
        return product

    async def get_reviews(product_id: int):
        try:
            response = await http_client.get(
                f"https://httpbin.org/get"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return []

    async def get_views(product_id: int):
        key = f"views/products/{product_id}"
        views = await async_redis_client.get(key)
        if views is None:
            await async_redis_client.setex(
                f"views/products/{product_id}", 300, 1)
            return 1
        else:
            await async_redis_client.setex(
                f"views/products/{product_id}", 300, int(views) + 1)
            return int(views) + 1

    product, reviews, views = await asyncio.gather(
        get_product(product_id),
        get_reviews(product_id),
        get_views(product_id),
    )
    if not product:
        return {"error": "Товар не найден"}
    return {"product": product, "reviews": reviews, "views": views}

@app.post("/orders/process")
async def process_orders_endpoint(orders_list: OrderProcessModel):
    try:
        orders_list = orders_list.order_list
        results = await process_orders(orders_list)
        return {"status": "success",
            "processed": len(results),
            "results": results}
    except Exception as e:
        return {"status": "error",
            "error": str(e)}

