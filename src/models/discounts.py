from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float, discount: float) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def apply(self, price: float, discount: float) -> float:
        if discount:
            return price * (1 - discount / 100)
        return price

class FixedDiscount(DiscountStrategy):
    def apply(self, price: float, discount: float) -> float:
        if discount:
            return price - discount
        return price