class Field:
    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.private_name)

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.private_name] = value

    def validate(self, value):
        pass

class UserField(Field):
    def validate(self, value):
        if not value:
            raise ValueError("Заказ должен иметь пользователя")

class ItemsField(Field):
    def validate(self, value):
        if not value:
            raise ValueError("Заказ не может быть пустым")

        for item in value:
            if item.quantity <= 0:
                raise ValueError("Количество товара должно быть положительным")