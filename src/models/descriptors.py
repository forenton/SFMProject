class PositiveNumber:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.value)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f'{self.value} не может быть отрицательным')
        setattr(instance, self.value, value)

class CachedProperty:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        cache_attr = f'__cached__{self.name}'
        if hasattr(instance, cache_attr):
            print('Cache')
            return getattr(instance, cache_attr)
        value = self.func(instance)
        setattr(instance, cache_attr, value)
        return value


class OrderValidator:
    """Класс для валидации заказа (SRP)"""
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.value)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f'{self.value} не может быть отрицательным')
        setattr(instance, self.value, value)

    @staticmethod
    def validate(order) -> bool:
        """Валидировать заказ"""
        if not order.items:
            raise ValueError("Заказ не может быть пустым")
        if not order.user:
            raise ValueError("Заказ должен иметь пользователя")
        for item in order.items:
            if item.quantity <= 0:
                raise ValueError("Количество товара должно быть положительным")
        return True