import src.models as model

def process_advanced_order_system():
    """Демонстрация всех продвинутых концепций ООП"""
    # 5. Дескрипторы для валидации
    product = model.Product("Ноутбук", 1000, 10)  # Автоматическая валидация
    items = [product] #исключительно для демонстрации
    user = model.User('1', '123', '123@', 19, 1000)
    # 1. Factory для создания заказов
    order = model.OrderFactory.create_order(1, items, user)

    # 2. Strategy для расчета доставки
    delivery = model.StandardDelivery()
    delivery_cost = delivery.calculate_cost(5.0)

    # 3. Полиморфизм для платежей
    payment = model.Payment('123', 2, 'Card_Payment')

    model.PaymentCalculator().process(payment)

    # 4. Метакласс для сериализации
    order_json = order.to_dict()

    # 6. Миксины для логирования
    model.PaymentCalculator().log("Платеж обработан")

    # 7. Магические методы
    print(len(order))  # Количество товаров
    print(product in order)  # Проверка наличия

    return {
        "order": order_json,
        "delivery_cost": delivery_cost,
        "product": product.to_dict()
    }

if __name__ == "__main__":
    print(process_advanced_order_system())