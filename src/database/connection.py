from typing import Optional

import psycopg2
from os import getenv
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import HTTPException
import asyncpg

load_dotenv()

DB_CONFIG = {
    "host": getenv("DB_HOST"),
    "port": getenv("DB_PORT"),
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
}
DB_REPLICA_CONFIG = {
    "host": getenv("DB_REPLICA_HOST"),
    "port": getenv("DB_REPLICA_PORT"),
    "database": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
}


DB_URL = ("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}").format(**DB_CONFIG)
engine = create_engine(url=DB_URL,
                       # echo=True
                       )
repeatable_engine = engine.execution_options(isolation_level="REPEATABLE READ")
session_maker = sessionmaker(bind=engine)
repeatable_read_session_maker = sessionmaker(bind=repeatable_engine)

ASYNC_DB_URL = ("postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}").format(**DB_CONFIG)
async_engine = create_async_engine(url=ASYNC_DB_URL)
async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

@contextmanager
def get_connection(read_only=False):
    conn = None
    try:
        if read_only:
            conn = psycopg2.connect(**DB_REPLICA_CONFIG)
        else:
            conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        if not read_only:
            conn.commit()
    except psycopg2.Error as e:
        if conn and not read_only:
            conn.rollback()
        print(f"Ошибка подключение к БД: {e}")
        raise
    finally:
        if conn:
            conn.close()

def test_connection():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Подключение успешно! Версия PostgreSQL: {version[0]}")

db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    """Инициализация пула при старте"""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            **DB_CONFIG,
            min_size=5,
            max_size=20
        )
    return db_pool


async def close_db_pool():
    """Закрытие пула при остановке"""
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None


async def get_db():
    """Зависимость для получения соединения из пула"""
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    async with db_pool.acquire() as conn:
        yield conn


async def get_pool():
    """Зависимость для получения самого пула"""
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_pool


if __name__ == "__main__":
    test_connection()
