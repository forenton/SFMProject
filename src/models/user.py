from src.models.metaclasses import Model
from src.services.user_services import UserNameValidator, UserEmailValidator, UserBalanceValidator, UserAgeValidator, UserCalculator


class User(Model):
    name = UserNameValidator()
    email = UserEmailValidator()
    balance = UserBalanceValidator()
    age = UserAgeValidator()

    def __init__(self, user_id, name, email, age, balance):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.balance = balance
        self.orders = []
        self.is_active = True

    def get_info(self):
        return "Пользователь: " + self.name + ", Email: " + self.email

if __name__ == "__main__":
    user = User('1', '123', '123@', 19, 1000)
    print(user.get_info())
    print(UserCalculator.calculate_total_spent(user))