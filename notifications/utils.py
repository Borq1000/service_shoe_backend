import json
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()

def get_status_message(status):
    """
    Возвращает понятное сообщение для каждого статуса заказа.
    """
    status_messages = {
        'pending': 'Заказ ожидает курьера',
        'courier_assigned': 'Курьер принял ваш заказ',
        'courier_on_the_way': 'Курьер выехал к вам',
        'at_location': 'Курьер прибыл на место',
        'courier_on_the_way_to_master': 'Курьер везет вашу обувь мастеру',
        'in_progress': 'Ваш заказ в работе у мастера',
        'completed': 'Заказ выполнен',
        'cancelled': 'Заказ отменен',
        'return': 'Оформлен возврат заказа'
    }
    return status_messages.get(status, 'Статус заказа изменен')

def send_order_notification(order, notification_type, title, message, recipient=None):
    """
    Отправляет уведомление о заказе через WebSocket и сохраняет в базу данных.
    
    Args:
        order: Объект заказа
        notification_type: Тип уведомления (должен соответствовать статусам заказа)
        title: Заголовок уведомления
        message: Текст уведомления
        recipient: Получатель уведомления (если None, уведомление отправляется в зависимости от типа)
    """
    try:
        channel_layer = get_channel_layer()
        
        if recipient:
            # Проверяем, разрешен ли тип уведомления для роли пользователя
            if notification_type not in Notification.get_allowed_types_for_user(recipient):
                logger.warning(
                    f"Notification type {notification_type} is not allowed for user {recipient.id} "
                    f"with role {recipient.user_type}"
                )
                return
            recipients = [recipient]
        elif notification_type == 'new_order':
            # Для новых заказов отправляем всем активным курьерам
            recipients = User.objects.filter(user_type='courier', is_active=True)
        else:
            # Для обновлений отправляем клиенту и назначенному курьеру
            recipients = []
            if order.customer:
                recipients.append(order.customer)
            if order.courier:
                recipients.append(order.courier)

        for recipient in recipients:
            # Проверяем, разрешен ли тип уведомления для роли пользователя
            if notification_type not in Notification.get_allowed_types_for_user(recipient):
                continue

            # Сохраняем уведомление в базу данных
            notification = Notification.objects.create(
                recipient=recipient,
                order=order,
                type=notification_type,
                title=title,
                message=message
            )

            # Отправляем через WebSocket
            try:
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{recipient.id}',
                    {
                        'type': 'notification_message',
                        'message': {
                            'id': notification.id,
                            'type': notification_type,
                            'title': title,
                            'message': message,
                            'order_id': order.id if order else None,
                            'order_status': order.status if order else None,
                            'created_at': notification.created_at.isoformat(),
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification to user {recipient.id}: {str(e)}")
                # Уведомление сохранено в БД, пользователь увидит его при следующем запросе

    except Exception as e:
        logger.error(f"Error in send_order_notification: {str(e)}")
        raise

def send_status_update_notification(order):
    """
    Отправляет уведомление об изменении статуса заказа.
    """
    status_message = get_status_message(order.status)
    send_order_notification(
        order=order,
        notification_type=order.status,
        title='Статус заказа изменен',
        message=status_message
    )

def send_system_notification(recipient, title, message):
    """
    Отправляет системное уведомление конкретному пользователю.
    """
    try:
        # Системные уведомления разрешены для всех ролей
        notification = Notification.objects.create(
            recipient=recipient,
            type='system',
            title=title,
            message=message
        )

        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{recipient.id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'id': notification.id,
                        'type': 'system',
                        'title': title,
                        'message': message,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to send system notification to user {recipient.id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in send_system_notification: {str(e)}")
        raise 