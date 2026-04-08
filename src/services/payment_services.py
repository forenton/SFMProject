from src.models.payment import Payment, CardPayment, BankTransferPayment, PaypalPayment

class PaymentValidator:
    ALLOWED_PAYMENTS = ["card", "paypal", "bank_transfer"]

    def validate(self, payment: Payment):
        if payment.amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if payment.payment_method not in self.ALLOWED_PAYMENTS:
            raise ValueError("Неизвестный метод оплаты")
        return True

class PaymentRepository:
    def _save_to_database(self, order_id):
        """Сохранение в БД"""
        print(f"Сохранение платежа {order_id} в MySQL")

class NotificationService:
    def _send_notification(self, order_id):
        """Отправка уведомления"""
        print(f"Отправка email о платеже {order_id}")

class PaymentProcessor(PaymentValidator, PaymentRepository, NotificationService):
    def process(self, payment: Payment):
        self.validate(payment)
        payment_processor = None
        if payment.payment_method == "card":
            payment_processor = CardPayment()
        elif payment.payment_method == "paypal":
            payment_processor = PaypalPayment()
        elif payment.payment_method == "bank_transfer":
            payment_processor = BankTransferPayment()
        if payment_processor:
            payment_processor.process(payment)
        else:
            return "Ошибка при проведении платежа"
        self._save_to_database(payment.order_id)
        self._send_notification(payment.order_id)
        return payment.status

if __name__ == "__main__":
    payment = Payment('112', 12, 'bank_transfer')
    payment_processor = PaymentProcessor()
    payment_processor.process(payment)