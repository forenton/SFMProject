from dataclasses import dataclass
from src.models.notifications import Notification
from src.models.discounts import DiscountStrategy, PercentageDiscount, FixedDiscount
from src.models.order import Order, OrderCalculator
from src.database.database import Database
from src.models.mixin import LoggableMixin
from src.models.user import User

@dataclass
class DiscountValue:
    high_total: float = 10000.0
    low_total: float = 1000.0
    mid_total: float = 5000.0
    high_discount: float = 15.0
    low_discount: float = 5.0
    mid_discount: float = 10.0

def check_user_balance(user, total):
    if user.balance < total:
        raise ValueError("Недостаточно средств")

class OrderService(LoggableMixin):
    """Сервис для обработки заказов (DIP)"""

    def __init__(self, notification_service: Notification, database: Database):
        self.notification_service = notification_service
        self.database = database

    def process_order(self, order: Order, discount: float, user: User, discount_strategy: DiscountStrategy = None):
        """Обработка заказа"""
        total = OrderCalculator.calculate_total(order)
        if isinstance(discount_strategy, PercentageDiscount):
            final_total = self.calculate_percentage_discount(total)
        elif isinstance(discount_strategy, FixedDiscount):
            final_total = OrderCalculator.calculate_discount(order, discount, discount_strategy)
        else:
            print("Скидка не применена")
            final_total = total
        check_user_balance(user, total)
        self.notification_service.send(order)
        self.database.save(order)
        self.log(f"Заказ {order.order_id} обработан: пользователь {order.user}, сумма {final_total}")
        return final_total

    @staticmethod
    def calculate_percentage_discount(total: float):
        discount_processor = PercentageDiscount()
        if total > DiscountValue.high_total:
            return discount_processor.apply(total, DiscountValue.high_total)
        elif total > DiscountValue.mid_total:
            return discount_processor.apply(total, DiscountValue.mid_total)
        elif total > DiscountValue.low_total:
            return discount_processor.apply(total, DiscountValue.low_total)
        return total


if __name__ == '__main__':
    user = User('1', '123', '123@', 19, 1000)



