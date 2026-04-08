from src.models.metaclasses import Model
from src.models.discounts import DiscountStrategy, PercentageDiscount, FixedDiscount
from src.models.mixin import LoggableMixin, SerializableMixin
from src.models.product import Product
from src.models.order_validator import Field, UserField, ItemsField

class Order(Model, LoggableMixin, SerializableMixin):
    """Класс только для хранения данных заказа (SRP)"""
    order_id = Field()
    items = ItemsField()
    users = UserField()

    def __init__(self, order_id: int, items: list[Product], user: str):
        self.order_id = order_id
        self.items = items  # Список товаров
        self.user = user

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __add__(self, other):
        new_items = self.items + other.items
        return Order(self.order_id, new_items, self.user)


class OrderCalculator:
    """Класс для расчетов заказа (SRP)"""

    @staticmethod
    def calculate_total(order: Order) -> float:
        """Рассчитать общую стоимость заказа"""
        total = 0
        for item in order.items:
            total += item.price * item.quantity
        return total

    @staticmethod
    def calculate_discount(order: Order, discount_strategy: DiscountStrategy, discount_amount: float) -> float:
        """Рассчитать стоимость со скидкой"""
        total = OrderCalculator.calculate_total(order)
        return discount_strategy.apply(total, discount_amount)


if __name__ == "__main__":
    # Использование
    product = Product("Ноутбук", 1000, 10)
    order = Order(1, [product], 'user')

    # Каждый класс отвечает за свою задачу
    total = OrderCalculator.calculate_total(order)
    print(total)

    discount = PercentageDiscount()
    print(OrderCalculator.calculate_discount(order, discount, 10))