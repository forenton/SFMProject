from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class DeliveryFee:
    express_delivery: int = 20
    standard_delivery: int = 10

class DeliveryStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, distance: float) -> float:
        pass

class StandardDelivery(DeliveryStrategy):
    def calculate_cost(self, distance: float) -> float:
        return distance * DeliveryFee.standard_delivery

class ExpressDelivery(DeliveryStrategy):
    def calculate_cost(self, distance: float) -> float:
        return distance * DeliveryFee.express_delivery