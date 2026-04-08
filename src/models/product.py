from src.models.mixin import LoggableMixin, ValidateMixin, SerializableMixin
from abc import ABC, abstractmethod
from src.models.metaclasses import Model
from src.models.descriptors import PositiveNumber, CachedProperty
from src.models.discounts import DiscountStrategy, PercentageDiscount, FixedDiscount

class Product(LoggableMixin, ValidateMixin, SerializableMixin, Model):
    price = PositiveNumber("_price")
    quantity = PositiveNumber("_quantity")

    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['name'], data['price'], data['quantity'])

    @CachedProperty
    def total_value(self) -> float:
        return product.price * product.quantity

class ProductCalculatorABC(ABC):
    @abstractmethod
    def calculate_discount(self, price: float, discount: float) -> float:
        pass

class ProductCalculator(ProductCalculatorABC, LoggableMixin):
    @staticmethod
    def calculate_discount(price: float, discount: float, discount_strategy: DiscountStrategy):
        return discount_strategy.apply(price, discount)



if __name__ == '__main__':
    product = Product("Ноутбук", 1000, 10)

    data = {'name': '1', 'price': 100, 'quantity': 2}
    product_2 = Product.from_dict(data)
    print(ProductCalculator.calculate_discount(100, 10, PercentageDiscount()))
    print(product_2.to_dict())
    print(Model._registry)
    print(product.total_value)