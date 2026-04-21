from fastapi import FastAPI, Depends, APIRouter, HTTPException, status, Request
import asyncio
import asyncpg
import httpx
from contextlib import asynccontextmanager
from src.database.connection import DB_CONFIG
from src.services.cach_service import async_redis_client
from src.database.async_repository import process_orders_async as process_orders
from typing import List
from src.database.async_repository import ProductRepository, create_user_in_db, read_user_in_db
from fastapi.middleware.cors import CORSMiddleware
from src.services.cach_service import CacheService
import logging
from src.services.timer_service import Timer
from src.api.schemas import *
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

class OrderProcessModel(BaseModel):
    order_list: List[int]

class ProductCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название товара")
    price: float = Field(..., gt=0, description="Цена товара (должна быть больше 0)")
    quantity: int = Field(..., ge=0, description="Количество на складе (не может быть отрицательным)")

class PaginationModel(BaseModel):
    skip: int = 0
    limit: int = 10

db_pool: asyncpg.Pool | None = None
http_client: httpx.AsyncClient | None = None
product_repository: ProductRepository = ProductRepository(db_pool)
cash_service = CacheService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global db_pool, http_client, product_repository
    # Создание пула при старте
    db_pool = await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=5,
        max_size=20
    )
    product_repository = ProductRepository(db_pool)
    http_client = httpx.AsyncClient(timeout=5.0)
    yield

    # Закрытие пула при остановке
    await db_pool.close()
    await http_client.aclose()
    print("Connection pool закрыт")

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
v1_router = APIRouter(prefix="/v1", tags=["v1"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    global logger
    logger.info(f"Запрос: {request.method} {request.url.path}")
    with Timer() as timer:
        response = await call_next(request)
    logger.info(f"Ответ: {response.status_code}, время: {timer.result:.3f} сек")
    response.headers["X-Process-Time"] = str(timer.result)
    return response

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

@app.get("/products")
def get_all_products(skip: int = 0, limit: int = 10):
    try:
        products = cash_service.get_cached_products()
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
        products.sort(key=lambda x: x["id"])
        result_products = products
        return result_products
    except Exception as e:
        raise


@v1_router.post("/products")
async def create_product(product: ProductCreateModel):
    id = await product_repository.create(product.name, product.price, product.quantity)
    return {"status": "success", "id": id}

@v1_router.post("/register")
async def create_user(user: UserCreate, conn=Depends(get_db)):
    hashed_password = hash_password(user.password)
    result = await create_user_in_db(conn, name=user.name, password=hashed_password, email=user.email)
    return {"status": "success", "result": result}

@v1_router.get("/login")
@limiter.limit("5/minute")
async def login_user(request: Request, usermane: str, password: str, conn=Depends(get_db)):
    result = await read_user_in_db(conn, name=usermane)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    authorisation = verify_password(password, result["password"])
    if authorisation:
        output = {"name": result["name"], "email": result["email"], "balance": result["balance"]}
        return {"status": "success", "result": output}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)

app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)