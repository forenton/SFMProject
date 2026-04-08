from src.models.order import Order
#Order валидируется через дескрипторы при создании

class OrderFactory:
    @staticmethod
    def create_order(order_id, items, user):
        order = Order(order_id, items, user)
        return order

    @classmethod
    def create_order_from_dict(cls, order_dict):
        return cls.create_order(**order_dict)
