from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.database.queries_orm import *
from src.services.cach_service import CacheService


app = FastAPI()
cash_service = CacheService()

@app.get("/products/{id}")
def get_product(product_id):
    product = get_product_from_db(product_id)
    if not isinstance(product, ValueError):
        return product
    else:
        return JSONResponse(status_code=404,  content= {"message": str(product)})


@app.get("/users/balance/{id}")
def get_user_balance(id):
    user = read_user(id)
    if not isinstance(user, ValueError):
        return {"username": user.name, "balance": user.balance}
    else:
        return JSONResponse(status_code=404,  content= {"message": str(user)})

@app.get("/products")
def get_all_products(skip: int = 0, limit: int = 10):
    products = cash_service.get_cached_products()
    if not isinstance(products, ValueError):
        products.sort(key=lambda x: x["id"])
        result_products = products[skip:limit]
        return result_products
    else:
        return JSONResponse(status_code=404,  content= {"message": str(products)})
