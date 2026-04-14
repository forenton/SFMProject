import asyncio
import aiohttp
import requests
from src.services.timer_service import Timer


async def fetch_url_async(session, url):
    # print("Начали запрос")
    async with session.get(url) as response:
        result = await response.json()
    # print("Закончили запрос")
    return result

async def fetch_multiple_urls_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


def fetch_url(urls: list):
    result = []
    for url in urls:
        result.append(requests.get(url).json())
    return result

if __name__ == "__main__":
    timer = Timer()
    urls = ["https://jsonplaceholder.typicode.com/todos/1", "https://jsonplaceholder.typicode.com/todos/2",
            "https://jsonplaceholder.typicode.com/todos/3", "https://jsonplaceholder.typicode.com/todos/4"]
    with timer:
        print(asyncio.run(fetch_multiple_urls_async(urls)))
    print(f"Время выполнения асинхронных запросов {round(timer.result, 3)}")
    with timer:
        print(fetch_url(urls))
    print(f"Время выполнения последовательных запросов {round(timer.result, 3)}")

