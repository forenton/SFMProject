from user import *
from order import *
from product import *


if __name__ == "__main__":
    user = User('1', '123', '123@', 19, 1000)
    product = Product("Ноутбук", 1000, 10)
    order = Order(1, [product], 'user')
    print(Model._registry)  