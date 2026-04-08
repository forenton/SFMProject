from dataclasses import fields

class LoggableMixin:
    @classmethod
    def log(cls, message: str):
        print(f'Вызвана {cls.__name__}: {message}')

class ValidateMixin:
    def validate(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, int | float) and value < 0:
                raise ValueError(f'{field.name} не может быть отрицательным')


    def is_valid(self):
        try:
            self.validate()
            return True
        except ValueError:
            return False

class SerializableMixin:
    def to_json(self):
        return {
            "class": self.__class__.__name__,
            "data": self.__dict__
        }