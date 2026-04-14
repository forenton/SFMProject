import asyncio
from src.services.timer_service import Timer


async def validate_order(order_id: int) -> dict:
    """Валидация заказа"""
    await asyncio.sleep(1)
    return {"order_id": order_id, "valid": True}


async def reserve_items(order_id: int) -> dict:
    """Резервирование товаров"""
    # raise ConnectionError("Ошибка: не удалось подключиться к БД")
    await asyncio.sleep(1.5)
    return {"order_id": order_id, "reserved": True}


async def verify_address(order_id: int) -> dict:
    """Проверка адреса доставки"""
    await asyncio.sleep(0.5)
    raise ValueError("Ошибка: адрес неверен")
    return {"order_id": order_id, "address_valid": True}


async def process_order_tg(order_id: int) -> dict:
    """Обработка заказа через TaskGroup"""
    results = {}
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(validate_order(order_id))
        task2 = tg.create_task(reserve_items(order_id))
        task3 = tg.create_task(verify_address(order_id))
    results["order_id"] = order_id
    results["valid"] = task1.result()
    results["reserved"] = task2.result()
    results["verify_address"] = task3.result()
    return results

async def main():
    try:
        result = await process_order_tg(10)
        print("Заказ обработан:", result)
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(exc)
    except* ConnectionError as con:
        for exc in con.exceptions:
            print(exc)



if __name__ == "__main__":
    timer = Timer()
    with timer as timer:
        asyncio.run(main())
    print(timer.result)