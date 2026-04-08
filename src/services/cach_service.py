import json
from datetime import datetime
import redis
from secrets import token_hex
from src.database.connection import session_maker
from src.database.models import Products
from src.database.queries import Timer


redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
class CacheService:
    def __init__(self, host = "localhost", port = 6379, db = 0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )


    def get_cached_products(self):
        cached_key = "products:all"
        cached_products = self.redis_client.get(cached_key)
        if cached_products:
            return json.loads(cached_products)
        with session_maker() as session:
            products = session.query(Products).all()
            db_products = [{"id": p.id,
                    "name": p.name,
                    "price": float(p.price),
                    "quantity": p.quantity,
                }
                for p in products]
            self.redis_client.setex(cached_key, 86400, json.dumps(db_products))
        return db_products

    def invalidate_cache_products(self):
        self.redis_client.delete("products:all")

    def get_cached_product(self, product_id):
        cached_key = f"products:{product_id}"
        cached_product = self.redis_client.get(cached_key)
        if cached_product:
            return json.loads(cached_product)
        with session_maker() as session:
            product = session.query(Products).filter(Products.id == product_id).first()
            db_product = {"id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "quantity": product.quantity,
                }
            self.redis_client.setex(cached_key, 86400, json.dumps(db_product))
            return product

    def create_user_session(self, user_id):
        session_token = token_hex(32)
        session_key = f"session:{session_token}"
        session_data = {"user_id": user_id,
                       "created_at": datetime.now().isoformat()}
        self.redis_client.setex(session_key,86400, json.dumps(session_data))

    def get_user_session(self, session_token):
        session_key = f"session:{session_token}"
        session_data = self.redis_client.get(session_key)
        if session_data:
            return json.loads(session_data)
        return None

    def delete_user_session(self, session_token):
        session_key = f"session:{session_token}"
        self.redis_client.delete(session_key)

if __name__ == '__main__':
    timer = Timer()
    cache_service = CacheService()
    with timer as timer:
        print(cache_service.get_cached_product(1))
        print(cache_service.get_cached_product(2))
    print(f"Время выполнения {round(timer.result, 4)} с")




