import json
from fastapi import FastAPI, Response, HTTPException, status, Header, APIRouter
from fastapi.responses import JSONResponse
from src.database.queries_orm import *
from src.services.cach_service import CacheService


app = FastAPI()
cash_service = CacheService()
v1_router = APIRouter(prefix="/v1", tags=["v1"])

def serialize_product(product):
    return {"id": product.id, "name": product.name,
            "price": float(product.price), "quantity": product.quantity}

def authenticate_user(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен аутентификации"
        )

@v1_router.get("/products/{id}")
def get_product(product_id, authorization: str = Header(None)):
    product = get_product_from_db(product_id)
    if not isinstance(product, ValueError):
        return product
    else:
        return JSONResponse(status_code=404,  content= {"message": str(product)})

v2_router = APIRouter(
    prefix="/v2",
    tags=["v2"]
)
@v2_router.get("/products/{id}")
def get_product(product_id, authorization: str = Header(None)):
    product = get_product_from_db(product_id)
    if not isinstance(product, ValueError):
        return Response(content=json.dumps({"product": serialize_product(product)}),
                        media_type="application/json",
                        headers={"Cache-Control": "max-age=3600"})
    else:
        return JSONResponse(status_code=404,  content= {"message": str(product)})


@app.get("/users/balance/{id}")
def get_user_balance(id):
    user = read_user(id)
    if not isinstance(user, ValueError):
        return {"status": 200, "response": {"username": user.name, "balance": user.balance}}
    else:
        return JSONResponse(status_code=404,  content= {"message": str(user)})

@app.get("/products")
def get_all_products(skip: int = 0, limit: int = 10):
    products = cash_service.get_cached_products()
    if not isinstance(products, ValueError):
        products.sort(key=lambda x: x["id"])
        result_products = products[skip:limit]
        return {"status": 200, "response": result_products}
    else:
        return JSONResponse(status_code=404,  content= {"message": str(products)})


app.include_router(v1_router)
app.include_router(v2_router)