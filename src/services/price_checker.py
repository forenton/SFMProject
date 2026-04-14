import asyncio
import random

async def check_supplier(name: str, product_id: int, delay: float, price: int):
    """Имитация запроса к поставщику"""
    await asyncio.sleep(delay)
    return {"supplier": name, "product_id": product_id, "price": price}

async def invalid_supplier():
    await asyncio.sleep(1)
    raise ConnectionError

async def find_best_price(product_id: int) -> dict:
    """Найти лучшую цену среди поставщиков"""
    # Имитация получения поставщиков
    suppliers = [{"name": "Vanya", "product_id": 15, "delay": float(0.5), "price": 100},
                 {"name": "Olga", "product_id": 15, "delay": float(0.5), "price": 150},
                 {"name": "Alexey", "product_id": 15, "delay": float(0.5), "price": 50}
                 ]
    tasks = [
        asyncio.create_task(check_supplier(**supplier)) for supplier in suppliers
    ]
    results = await asyncio.gather(*tasks, invalid_supplier(), return_exceptions=True)
    best_price = results[0]["price"]
    best_supplier = None
    for result in results:
        if isinstance(result, Exception):
            continue
        elif result.get("price", None) < best_price:
            best_supplier = result

    return best_supplier

async def order_producer(queue: asyncio.Queue, num_orders: int, num_workers: int):
    """Генерация заказов"""
    for i in range (num_orders):
        order = {"id": i + 1, "total": random.randint(100, 10000)}
        await queue.put(order)
        print(f"Новый заказ #{order["id"]}: сумма заказа: {order["total"]}")
        await asyncio.sleep(0.5)
    for _ in range(num_workers):
        await queue.put(None)



async def order_worker(name: str, queue: asyncio.Queue):
    """Обработка заказов из очереди"""
    while True:
        order = await queue.get()
        if order is None:
            print(f"Обработчик {name} завершил работу")
            break
        print(f"Обработчик {name}: обработка заказа #{order['id']}...")
        await asyncio.sleep(1)
        print(f"Обработчик {name}: заказ #{order['id']} готов")

        queue.task_done()
    pass


async def main():
    queue = asyncio.Queue(maxsize=5)
    num_workers = 3
    num_orders = 10
    await asyncio.gather(order_producer(queue, num_orders, num_workers),
                         order_worker("1", queue),
                         order_worker("2", queue),
                         order_worker("3", queue))





if __name__ == "__main__":
    print(asyncio.run(find_best_price(15)))
    asyncio.run(main())


