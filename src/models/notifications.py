from abc import ABC, abstractmethod

class Notification(ABC):
    """Абстрактный класс для уведомлений"""
    @abstractmethod
    def send(self, order):
        pass

class EmailNotification(Notification):
    def __init__(self, order):
        self.order = order

    def send(self, message: str):
        print(f'Sending Email {message} to {self.order.user}')

class SMSNotification(Notification):
    def __init__(self, order):
        self.order = order

    def send(self, message: str):
        print(f'Sending SMS {message} to {self.order.user}')

def send_notifications(notification_list: list[Notification], message: str):
    for notification in notification_list:
        notification.send(message)



if __name__ == '__main__':
    pass