import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Получаем токен из query параметров
            token = self.scope['query_string'].decode().split('=')[1]
            # Проверяем токен и получаем пользователя
            user = await self.get_user_from_token(token)
            
            if user:
                self.user = user
                self.room_group_name = f'notifications_{user.id}'
                
                # Присоединяемся к группе пользователя
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        except (IndexError, TokenError):
            await self.close()

    async def disconnect(self, close_code):
        # Покидаем группу при отключении
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Обработка входящих сообщ��ний (если нужно)
        pass

    async def notification_message(self, event):
        """
        Отправляет уведомление клиенту с учетом его роли.
        """
        message = event['message']
        
        # Проверяем, разрешено ли уведомление для роли пользователя
        allowed_types = await self.get_allowed_notification_types(self.user)
        if message['type'] not in allowed_types:
            return  # Не отправляем уведомление, если тип не разрешен для роли

        # Отправляем уведомление
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Декодируем JWT токен
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return get_user_model().objects.get(id=user_id)
        except (TokenError, get_user_model().DoesNotExist):
            return None

    @database_sync_to_async
    def get_allowed_notification_types(self, user):
        """
        Возвращает разрешенные типы уведомлений для пользователя.
        """
        return Notification.get_allowed_types_for_user(user) 