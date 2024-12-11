from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

class Notification(models.Model):
    # Типы уведомлений для курьеров
    COURIER_NOTIFICATION_TYPES = {
        'new_order',              # Новый заказ
        'order_cancelled',        # Отмена заказа
        'system'                  # Системные уведомления
    }

    # Типы уведомлений для клиентов
    CLIENT_NOTIFICATION_TYPES = {
        'courier_assigned',             # Курьер назначен
        'courier_on_the_way',          # Курьер в пути
        'at_location',                 # Курьер на месте
        'courier_on_the_way_to_master', # Курьер везет заказ мастеру
        'in_progress',                 # Заказ в работе у мастера
        'completed',                   # Заказ выполнен
        'cancelled',                   # Заказ отменен
        'return',                      # Возврат заказа
        'system'                       # Системные уведомления
    }

    NOTIFICATION_TYPES = [
        ('new_order', 'Новый заказ'),
        ('courier_assigned', 'Курьер назначен'),
        ('courier_on_the_way', 'Курьер в пути'),
        ('at_location', 'Курьер на месте'),
        ('courier_on_the_way_to_master', 'Курьер везет заказ мастеру'),
        ('in_progress', 'Заказ в работе у мастера'),
        ('completed', 'Заказ выполнен'),
        ('cancelled', 'Заказ отменен'),
        ('return', 'Возврат заказа'),
        ('system', 'Системное уведомление')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f"{self.type} - {self.recipient.email} - {self.created_at}"

    @classmethod
    def get_allowed_types_for_user(cls, user):
        """
        Возвращает список разрешенных типов уведомлений для пользователя
        в зависимости от его роли.
        """
        if user.user_type == 'courier':
            return cls.COURIER_NOTIFICATION_TYPES
        return cls.CLIENT_NOTIFICATION_TYPES
