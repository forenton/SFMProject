from abc import ABC, abstractmethod
from src.models.order import Order


class Database(ABC):
    @abstractmethod
    def save(self, order: Order) -> float:
        pass