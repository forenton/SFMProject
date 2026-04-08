from src.models.order_validator import Field
from src.models.order import OrderCalculator, Order
from src.models.discounts import DiscountStrategy
from src.models.notifications import Notification
from src.database.database import Database

class UserNameValidator(Field):
    def validate(self, value):
        if not value:
            raise ValueError("Имя не может быть пустым")
        return True

class UserEmailValidator(Field):
    def validate(self, value):
        if "@" not in value:
            raise ValueError("Email должен содержать @")
        return True

class UserBalanceValidator(Field):
    def validate(self, value):
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")

class UserAgeValidator(Field):
    def validate(self, value):
        if value < 18:
            raise ValueError("Пользователь должен быть старше 18 лет")
        return True

class UserCalculator:
    @staticmethod
    def calculate_total_spent(user):
        """Расчет общей потраченной суммы"""
        total = 0
        for order in user.orders:
            total += OrderCalculator.calculate_total(order)
        return total

    def apply_discount(self, user, discount_strategy: DiscountStrategy, value):
        """Применение скидки к балансу"""
        if isinstance(discount_strategy, DiscountStrategy):
            user.balance += discount_strategy.apply(value)
        else:
            raise ValueError("Неизвестный тип скидки")

class UserWelcomeNotification(Notification):
    @staticmethod
    def send_welcome_email(user):
        print(f"Отправка email на {user.email}: Добро пожаловать, {user.name}!")

class UserDatabase(Database):
    @staticmethod
    def save(user):
        print(f"Сохранение пользователя {user.user_id} в MySQL")

class UserService:
    @staticmethod
    def generate_report(user):
        """Генерация отчета"""
        report = f"Пользователь: {user.name}\n"
        report += f"Email: {user.email}\n"
        report += f"Всего заказов: {len(user.orders)}\n"
        report += f"Потрачено: {UserCalculator.calculate_total_spent(user)}\n"
        print(report)
        return report

if __name__ == "__main__":
    pass