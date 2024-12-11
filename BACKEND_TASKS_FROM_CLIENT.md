# Задачи по доработке бэкенда

## 1. Приложение notifications

### Модели

```python
class Notification(models.Model):
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('new_order', 'Новый заказ'),
        ('order_update', 'Обновление заказа'),
        ('order_cancelled', 'Отмена заказа'),
        ('system', 'Системное уведомление')
    ])
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### API Endpoints

1. `GET /api/notifications/` - Получение списка уведомлений
2. `PATCH /api/notifications/{id}/read/` - Отметить уведомление как прочитанное
3. `DELETE /api/notifications/{id}/` - Удалить уведомление
4. `GET /api/notifications/unread-count/` - Получить количество непрочитанных уведомлений

### WebSocket Events

1. Настроить Django Channels для WebSocket соединений
2. Создать consumer для обработки уведомлений
3. Реализовать группы для уведомлений по типам пользователей

## 2. Расширение API заказов

### Новые эндпоинты

1. `GET /api/orders/courier/statistics/` - Статистика курьера
   ```python
   {
       "totalOrders": int,
       "completedOrders": int,
       "cancelledOrders": int,
       "rating": float,
       "earnings": decimal,
       "ordersByDay": [
           {
               "date": "YYYY-MM-DD",
               "count": int
           }
       ]
   }
   ```

### Расширение существующих эндпоинтов

1. `GET /api/orders/courier/orders/` - Добавить параметры:
   - `search` - поиск по адресу
   - `status` - фильтр по статусу
   - `sort_by` - сортировка (date_asc, date_desc, distance_asc, distance_desc)
   - `distance` - максимальное расстояние в км
   - `latitude`, `longitude` - координаты для расчета расстояния

## 3. Расширение профиля пользователя

### Модели

```python
class UserPrivacySettings(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    show_phone = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_rating = models.BooleanField(default=True)
```

### API Endpoints

1. `PATCH /authentication/profile/image/` - Загрузка фото профиля

   - Добавить поддержку multipart/form-data
   - Валидация изображений
   - Создание миниатюр

2. `PATCH /authentication/profile/privacy/` - Обновление настроек приватности
   ```python
   {
       "show_phone": bool,
       "show_email": bool,
       "show_rating": bool
   }
   ```

## 4. Интеграция с WebSocket

### Настройка ASGI

1. Настроить Django Channels
2. Создать маршрутизацию для WebSocket
3. Настроить аутентификацию через JWT в WebSocket

### События для отправки

1. `new_order` - Новый заказ доступен
2. `order_updated` - Обновление статуса заказа
3. `order_cancelled` - Отмена заказа

## 5. Оптимизация производительности

1. Добавить кэширование для:

   - Статистики курьера
   - Списка заказов
   - Профиля пользователя

2. Оптимизировать запросы:
   - Использовать select_related/prefetch_related
   - Добавить индексы для часто используемых полей
   - Оптимизировать географические запросы

## 6. Безопасность

1. Добавить rate limiting для API endpoints
2. Валидация входных данных
3. Проверка прав доступа для всех новых эндпоинтов
4. Логирование важных действий

## 7. Тестирование

1. Написать unit-тесты для:

   - Моделей уведомлений
   - API эндпоинтов
   - WebSocket consumers

2. Написать интеграционные тесты для:
   - WebSocket соединений
   - Фильтрации и поиска заказов
   - Загрузки изображений
