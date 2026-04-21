from typing import List

from fastapi import FastAPI, HTTPException, APIRouter, Depends
from src.database.async_repository import get_orders_repository, OrdersRepository
import asyncio
from src.api.schemas import CreateOrderModel

orders_router = APIRouter(prefix="/orders", tags=["orders"])

@orders_router.get("/")
async def get_orders(order_id: int, order_repository: OrdersRepository = Depends(get_orders_repository)):
    orders = await order_repository.get_order_from_db(order_id)
    return orders

@orders_router.post("/")
async def create_order(
        order: CreateOrderModel,
        order_repository: OrdersRepository = Depends(get_orders_repository)):
    await order_repository.create_order(order.user_id, order.product_list)
    return {"status": "ok"}


if __name__ == "__main__":
    pass