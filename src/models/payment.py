from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.models.mixin import LoggableMixin, SerializableMixin

@dataclass
class Payment:
    order_id: str
    amount: int
    payment_method: str
    status: str = "pending"

class PaymentMethod(ABC, LoggableMixin, SerializableMixin):
    @abstractmethod
    def process(self, payment: Payment):
        pass

class CardPayment(PaymentMethod):
    def process(self, payment: Payment):
        super().log('Оплата картой')
        if payment.amount > 10000:
            fee = payment.amount * 0.02
        else:
            fee = payment.amount * 0.03
        result = self._charge_card(payment.amount + fee)
        if result:
            payment.status = "completed"
            print(f"Платеж по карте обработан: {payment.amount + fee}")
        else:
            payment.status = "failed"
            raise ValueError("Ошибка обработки карты")

    def _charge_card(self, amount):
        """Зарядка карты"""
        print(f"Зарядка карты на сумму {amount}")
        return True

class PaypalPayment(PaymentMethod):
    def process(self, payment: Payment):
        super().log('Оплата Paypal')
        fee = payment.amount * 0.035
        result = self._charge_paypal(payment.amount + fee)
        if result:
            payment.status = "completed"
            print(f"Платеж через PayPal обработан: {payment.amount + fee}")
        else:
            payment.status = "failed"
            raise ValueError("Ошибка обработки PayPal")

    def _charge_paypal(self, amount):
        """Зарядка PayPal"""
        print(f"Зарядка PayPal на сумму {amount}")
        return True

class BankTransferPayment(PaymentMethod):
    def process(self, payment: Payment):
        super().log('Оплата банковским переводом')
        fee = 50  # Фиксированная комиссия
        result = self._process_bank_transfer(payment.amount + fee)
        if result:
            payment.status = "completed"
            print(f"Банковский перевод обработан: {payment.amount + fee}")
        else:
            payment.status = "failed"
            raise ValueError("Ошибка банковского перевода")

    def _process_bank_transfer(self, amount):
        """Обработка банковского перевода"""
        print(f"Банковский перевод на сумму {amount}")
        return True

PAYMENT_METHODS = {'CARD_PAYMENT': CardPayment(),
                   'BANK_TRANSFER_PAYMENT': BankTransferPayment(),
                   'PAYPAL_PAYMENT': PaypalPayment()}

class PaymentCalculator(LoggableMixin):
    def process(self, payment: Payment):

        super().log('Калькулятор платежа')
        payment_method = PAYMENT_METHODS.get(payment.payment_method.upper(), False)
        if payment_method:
            result = payment_method.process(payment)
        return result

if __name__ == "__main__":
    payment = Payment('123', 2, 'Card_Payment')
    p = PaymentCalculator()
    print(p.process(payment))

