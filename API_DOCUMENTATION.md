# Техническая документация API Shoe Service

## Базовый URL

Все запросы к API должны быть отправлены на базовый URL:

```
http://127.0.0.1:8000
```

## WebSocket для уведомлений

### Подключение к WebSocket

URL для подключения:

```
ws://127.0.0.1:8000/ws/notifications/
```

**Важно:** Бэкенд использует нативные WebSocket (не Socket.IO).

### Пример реализации WebSocket клиента

```javascript
class NotificationWebSocket {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3 секунды
  }

  connect() {
    const token = localStorage.getItem("access_token"); // Получаем JWT токен

    // Создаем WebSocket соединение с токеном
    this.socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
    );

    // Обработчик успешного подключения
    this.socket.onopen = () => {
      console.log("WebSocket соединение установлено");
      this.reconnectAttempts = 0; // Сбрасываем счетчик попыток
    };

    // Обработчик входящих сообщений
    this.socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data);
        this.handleNotification(notification);
      } catch (error) {
        console.error("Ошибка при обработке уведомления:", error);
      }
    };

    // Обработчик ошибок
    this.socket.onerror = (error) => {
      console.error("Ошибка WebSocket:", error);
    };

    // Обработчик закрытия соединения
    this.socket.onclose = (event) => {
      console.log("WebSocket соединение закрыто:", event.code, event.reason);
      this.handleDisconnect();
    };
  }

  // Обработка входящих уведомлений
  handleNotification(notification) {
    console.log("Получено новое уведомление:", notification);

    // Пример обработки разных типов уведомлений
    switch (notification.type) {
      case "new_order":
        // Обработка нового заказа
        this.handleNewOrder(notification);
        break;
      case "order_update":
        // Обработка обновления заказа
        this.handleOrderUpdate(notification);
        break;
      case "order_cancelled":
        // Обработка отмены заказа
        this.handleOrderCancellation(notification);
        break;
      case "system":
        // Обработка системного уведомления
        this.handleSystemNotification(notification);
        break;
    }
  }

  // Пример обработчиков разных типов уведомлений
  handleNewOrder(notification) {
    // Показать уведомление о новом заказе
    this.showNotification("Новый заказ", notification.message);
  }

  handleOrderUpdate(notification) {
    // Обновить статус заказа в интерфейсе
    this.showNotification("Обновление заказа", notification.message);
  }

  handleOrderCancellation(notification) {
    // Показать уведомление об отмене
    this.showNotification("Заказ отменен", notification.message);
  }

  handleSystemNotification(notification) {
    // Показать системное уведомление
    this.showNotification("Системное уведомление", notification.message);
  }

  // Показ уведомления (пример)
  showNotification(title, message) {
    // Можно использовать любую библиотеку для уведомлений
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, { body: message });
    }
  }

  // Обработка отключения и переподключение
  handleDisconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Попытка переподключения ${this.reconnectAttempts} из ${this.maxReconnectAttempts}`
      );

      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error(
        "Превышено максимальное количество попыток переподключения"
      );
    }
  }

  // Закрытие соединения
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// Пример использования
const notificationSocket = new NotificationWebSocket();

// Подключение при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  notificationSocket.connect();
});

// Отключение при уходе со страницы
window.addEventListener("beforeunload", () => {
  notificationSocket.disconnect();
});

// Запрос разрешения на показ уведомлений
if ("Notification" in window) {
  Notification.requestPermission();
}
```

### Формат уведомлений

Входящие уведомления имеют следующий формат:

```javascript
{
    "id": 1,
    "title": "Новый заказ",
    "message": "Появился новый заказ на услугу Чистка обуви",
    "type": "new_order",
    "order": {
        "id": 123,
        "service": "Чистка обуви",
        "status": "pending"
    },
    "is_read": false,
    "created_at": "2024-12-10T12:00:00Z"
}
```

### Типы уведомлений

1. **new_order** - Новый заказ

   - Отправляется всем активным курьерам
   - Содержит информацию о новом заказе

2. **order_update** - Обновление заказа

   - Отправляется клиенту и назначенному курьеру
   - Содержит информацию об и��менении статуса

3. **order_cancelled** - Отмена заказа

   - Отправляется клиенту и курьеру (если назначен)
   - Содержит причину отмены

4. **system** - Системное уведомление
   - Может быть отправлено любому пользователю
   - Содержит системную информацию

### Обработка ошибок

1. **Потеря соединения**

   - Автоматические попытки переподключения
   - Максимум 5 попыток с интервалом 3 секунды

2. **Ошибки аутентификации**

   - Код 4003: Невалидный токен
   - Необходимо обновить токен и переподключиться

3. **Ошибки формата данных**
   - Всегда проверяйте формат входящих данных
   - Используйте try-catch при парсинге JSON

## 1. Модели

### Модель пользователя (User)

```python
class User:
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    user_type = models.CharField(choices=['client', 'courier', 'admin'], default='client')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
```

### Модели услуг

```python
class Service:
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='services/icons/%Y/%m')
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True)

class Attribute:
    name = models.CharField(max_length=100)

class ServiceAttribute:
    service = models.ForeignKey(Service)
    attribute = models.ForeignKey(Attribute)
    value = models.CharField(max_length=100)

class Option:
    name = models.CharField(max_length=100)

class ServiceOption:
    service = models.ForeignKey(Service)
    option = models.ForeignKey(Option)
    value = models.CharField(max_length=100)
```

### Модель заказа

```python
class Order:
    service = models.ForeignKey(Service, related_name='orders')
    customer = models.ForeignKey(User, related_name='orders_as_customer')
    courier = models.ForeignKey(User, null=True, related_name='orders_as_courier')
    city = models.CharField(max_length=100, default="Москва")
    street = models.CharField(max_length=255)
    building_num = models.CharField(max_length=50, null=True)
    building = models.CharField(max_length=50, null=True)
    floor = models.CharField(max_length=50, null=True)
    apartment = models.CharField(max_length=50, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    status = models.CharField(choices=[
        'pending', 'courier_assigned', 'courier_on_the_way',
        'at_location', 'courier_on_the_way_to_master',
        'in_progress', 'completed', 'cancelled', 'return'
    ])
    status_changed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)
    image = models.ImageField(upload_to='orders/images/%Y/%m/%d/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

### Модель уведомления

```python
class Notification:
    recipient = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(choices=[
        ('new_order', 'Новый заказ'),
        ('order_update', 'Обновление заказа'),
        ('order_cancelled', 'Отмена заказа'),
        ('system', 'Системное уведомление')
    ])
    order = models.ForeignKey(Order, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 2. Конечные точки API

### Аутентификация

Базовый URL: `/authentication/`

#### Регистрация и аутентификация

- `POST /register/` - Регистрация нового пользователя

  ```json
  {
    "email": "string",
    "first_name": "string",
    "password": "string",
    "confirm_password": "string",
    "user_type": "client|courier|admin"
  }
  ```

- `POST /api/token/` - Получение JWT токена

  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```

  Ответ:

  ```json
  {
    "access": "string",
    "refresh": "string",
    "id": "number",
    "email": "string"
  }
  ```

- `POST /api/token/refresh/` - Обновление JWT токена
- `POST /api/token/verify/` - Проверка JWT токена

#### Сброс пароля

- `POST /password-reset-request/` - Запрос на сброс пароля
- `POST /reset-password/<uidb64>/<token>/` - Сброс пароля

#### Управление профилем

- `GET /profile/` - Получение профиля пользователя
- `PATCH /profile/` - Обновление профиля пользователя
  ```json
  {
    "first_name": "string",
    "last_name": "string",
    "phone": "string"
  }
  ```
- `PATCH /profile/image/` - Обновление изображения профиля

  ```http
  Content-Type: multipart/form-data

  image: [файл изображения]
  ```

  Ответ успешной загрузки:

  ```json
  {
    "message": "Profile image updated successfully"
  }
  ```

  Возможные ошибки:

  ```json
  {
    "error": "No image provided"
  }
  // или
  {
    "error": "File size exceeds 5MB limit"
  }
  // или
  {
    "error": "Invalid image format. Allowed formats: JPEG, JPG, PNG, GIF, WebP"
  }
  ```

  Ограничения:

  - Максимальный размер файла: 5MB
  - Поддерживаемые форматы: JPEG, JPG, PNG, GIF, WebP
  - Требуется аутентификация

### Услуги

Базовый URL: `/api/services/`

#### Услуги

- `GET /services/` - Список всех услуг
- `GET /services/{slug}/` - Детали услуги
- `POST /services/` - Создание услуги (только админ)
- `PUT /services/{slug}/` - Обновление услуги (только админ)
- `DELETE /services/{slug}/` - Удаление услуги (только админ)

Формат ответа:

```json
{
  "id": "number",
  "name": "string",
  "description": "string",
  "price": "decimal",
  "attributes": [
    {
      "attribute": "string",
      "value": "string"
    }
  ],
  "options": [
    {
      "option": "string",
      "value": "string"
    }
  ],
  "image": "url",
  "slug": "string"
}
```

#### Атрибуты и опции

- `GET /attributes/` - Список всех атрибутов
- `GET /options/` - Список всех опций

### Заказы

Базовый URL: `/api/orders/`

#### Заказы клиентов

- `GET /client/orders/` - Список заказов клиента
- `POST /client/orders/` - Создание нового заказа
- `GET /client/orders/{id}/` - Детали заказа
- `PUT /client/orders/{id}/` - Обновление заказа
- `DELETE /client/orders/{id}/` - Удаление заказа

Данные для создания заказа:

```json
{
  "service": "number",
  "city": "string",
  "street": "string",
  "building_num": "string",
  "building": "string",
  "floor": "string",
  "apartment": "string",
  "latitude": "number",
  "longitude": "number",
  "comment": "string",
  "image": "file"
}
```

#### Заказы курьеров

- `GET /courier/orders/` - Список доступных заказов
- `GET /courier/orders/assigned_orders/` - Список назначенных заказов
- `GET /courier/orders/completed_orders/` - Список завершенных заказов
- `PATCH /courier/orders/{id}/assign/` - Назначить заказ себе
- `PATCH /courier/orders/{id}/unassign/` - Отменить назначение заказа
- `PATCH /courier/orders/{id}/update_status/` - Обновить статус заказа
  ```json
  {
    "status": "courier_assigned|courier_on_the_way|at_location|courier_on_the_way_to_master|in_progress|completed"
  }
  ```

### Уведомления

Базовый URL: `/api/notifications/`

#### REST API

- `GET /notifications/` - Получение списка уведомлений

  ```json
  [
    {
      "id": "number",
      "title": "string",
      "message": "string",
      "type": "new_order|order_update|order_cancelled|system",
      "order": "number|null",
      "is_read": "boolean",
      "created_at": "datetime"
    }
  ]
  ```

- `PATCH /notifications/{id}/read/` - Отметить уведомление как прочитанное
- `DELETE /notifications/{id}/` - Удалить уведомление
- `GET /notifications/unread-count/` - Получить количество непрочитанных уведомлений
  ```json
  {
    "unread_count": "number"
  }
  ```

#### WebSocket

URL подключения: `ws://your-domain/ws/notifications/`

Формат получаемых сообщений:

```json
{
  "id": "number",
  "title": "string",
  "message": "string",
  "type": "new_order|order_update|order_cancelled|system",
  "order": "number|null",
  "is_read": false,
  "created_at": "datetime"
}
```

## 3. Аутентификация и права доступа

### Аутентификация

- Используется JWT (JSON Web Token) аутентификация
- Токены должны быть включены в заголовок Authorization: `Authorization: Bearer <token>`
- Токены доступа имеют ограниченный срок действия
- Refresh токены можно использовать для получения новых токенов доступа
- WebSocket соединения также требуют JWT аутентификации

### Типы пользователей и права доступа

1. Клиент

   - Может создавать и управлять своими заказами
   - Может просматривать свой профиль и историю заказов
   - Получает уведомления об обновлениях своих заказов
   - Не имеет доступа к эндпоинтам курьера

2. Курьер

   - Может просматривать доступные заказы
   - Может назначать/отменять назначение заказов себе
   - Может обновлять статус заказа
   - Получает уведомления о новых заказах
   - Не может создавать заказы
   - Не имеет доступа к эндпоинтам клиента

3. Администратор
   - Полный доступ ко всем эндпоинтам
   - Может управлять услугами, атрибутами и опциями
   - Доступ к интерфейсу администратора Django

## 4. Дополнительные функции

### Пагинация

- Размер страницы по умолчанию: 10 элементов
- Параметры запроса:
  - `page`: Номер страницы
  - `page_size`: Количество элементов на странице

### Загрузка файлов

- Изображения услуг: `services/icons/%Y/%m`
- Изображения заказов: `orders/images/%Y/%m/%d/`
- Поддерживаемые форматы: Стандартные форматы изображений

### Поток статусов заказа

```
pending -> courier_assigned -> courier_on_the_way -> at_location ->
courier_on_the_way_to_master -> in_progress -> completed
```

- Статус можно откатить в течение 10 минут после изменения
- Разрешены только последовательные изменения статуса
- Каждое изменение статуса генерирует уведомление

### Обработка ошибок

- Используются стандартные HTTP коды состояния
- Подробные сообщения об ошибках в теле ответа
- Ошибки валидации возвращают 400 Bad Request
- Ошибки аутентификации возвращают 401 Unauthorized
- Ошибки пра�� доступа возвращают 403 Forbidden

### Real-time уведомления

- WebSocket для мгновенных уведомлений
- Автоматическая отправка уведомлений при:
  - Создании нового заказа (для курьеров)
  - Изменении статуса заказа
  - Назначении курьера
  - Системных событиях
- Сохранение всех уведомлений базе данных
- Возможность отметить уведомления как прочитанные
- Счетчик непрочитанных уведомлений

## Загрузка файлов

### Общие правила

- Максимальный размер файла: 5MB
- Поддерживаемые форматы: JPEG, JPG, PNG, GIF, WebP
- Content-Type: multipart/form-data
- Файлы сохраняются в директориях по датам

### Загрузка изображений для заказов

Endpoint: `POST /api/orders/client/orders/`

```http
POST /api/orders/client/orders/ HTTP/1.1
Content-Type: multipart/form-data
Authorization: Bearer <your-token>

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="service"

1
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="city"

Москва
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="street"

Ленина
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="shoe.jpg"
Content-Type: image/jpeg

[binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Пример ответа:

```json
{
  "id": 1,
  "service": 1,
  "city": "Москва",
  "street": "Ленина",
  "image": "http://127.0.0.1:8000/media/orders/images/2024/12/10/shoe.jpg"
  // ... другие поля заказа
}
```

### Пример загрузки на фронтенде

```javascript
// Создание FormData с файлом и данными заказа
const formData = new FormData();
formData.append("service", serviceId);
formData.append("city", city);
formData.append("street", street);
formData.append("image", imageFile); // imageFile - объект File из input[type="file"]

// Отправка запроса
const response = await fetch(
  "http://127.0.0.1:8000/api/orders/client/orders/",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      // Не указывайте Content-Type, он будет установлен автоматически
    },
    body: formData,
  }
);

const data = await response.json();
const imageUrl = data.image; // URL загруженного изображения
```

### Валидация файлов

Сервер проверяет:

- Размер файла (не более 5MB)
- Тип файла (только изображения)
- MIME-тип файла
- Расширение файла

Возможные ошибки:

```json
{
  "image": [
    "Файл слишком большой. Максимальный размер 5MB.",
    "Неподдерживаемый формат файла. Разрешены: JPEG, JPG, PNG, GIF, WebP",
    "Это поле обязательно."
  ]
}
```

### React-компонент для загрузки

```javascript
import React, { useState } from "react";

const ImageUpload = ({ onUpload }) => {
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setError(null);

    // Проверка рамера
    if (file.size > 5 * 1024 * 1024) {
      setError("Файл слишком большой. Максимальный размер 5MB");
      return;
    }

    // Проверка типа
    if (!file.type.match("image.*")) {
      setError("Можно загружать только изображения");
      return;
    }

    // Предпросмотр
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);

    // Передача файла родительскому компоненту
    onUpload(file);
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleFileSelect} />
      {error && <div className="error">{error}</div>}
      {preview && (
        <div>
          <img src={preview} alt="Preview" style={{ maxWidth: "200px" }} />
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
```

### Использование компонента

```javascript
const OrderForm = () => {
  const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append("service", serviceId);
    formData.append("image", file);
    // ... добавление других полей

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/orders/client/orders/",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.image?.[0] || "Ошибка загрузки");
      }

      // Обработка успешной загрузки
      console.log("Изображение загружено:", data.image);
    } catch (error) {
      console.error("Ошибка:", error);
    }
  };

  return (
    <form>
      <ImageUpload onUpload={handleImageUpload} />
      {/* Другие поля формы */}
    </form>
  );
};
```

### Загрузка изображения профиля

Endpoint: `PATCH /authentication/profile/image/`

Запрос:

```http
PATCH /authentication/profile/image/ HTTP/1.1
Content-Type: multipart/form-data
Authorization: Bearer <your-token>

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="profile.jpg"
Content-Type: image/jpeg

[binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Успешный ответ (200 OK):

```json
{
  "image": "http://127.0.0.1:8000/media/profile_images/2024/12/profile.jpg"
}
```

Ошибки:

```json
{
    "error": "Файл изображения не предоставлен"
}
// или
{
    "error": "Размер изображения не должен превышать 5MB"
}
// или
{
    "error": "Неверный формат изображения. Разрешенные форматы: JPEG, JPG, PNG, GIF, WebP"
}
```

### Пример загрузки изображения профиля на React

```javascript
const ProfileImageUpload = () => {
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);

    // Проверка размера
    if (file.size > 5 * 1024 * 1024) {
      setError("Размер файла не должен превышать 5MB");
      setLoading(false);
      return;
    }

    // Проверка типа
    if (!file.type.match("image.*")) {
      setError("Можно загружать только изображения");
      setLoading(false);
      return;
    }

    // Создание превью
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);

    // Отправка на сервер
    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/authentication/profile/image/",
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Ошибка загрузки изображения");
      }

      // Обновление изображения профиля в интерфейсе
      setPreview(data.image);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        disabled={loading}
      />
      {error && <div className="error">{error}</div>}
      {loading && <div>Загрузка...</div>}
      {preview && (
        <div>
          <img
            src={preview}
            alt="Profile"
            style={{
              width: "150px",
              height: "150px",
              objectFit: "cover",
              borderRadius: "50%",
            }}
          />
        </div>
      )}
    </div>
  );
};

export default ProfileImageUpload;
```

## Заказы (Orders)

### Эндпоинты для клиентов

#### Получение всех заказов клиента

```http
GET /api/orders/client/orders/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "service": {
      "id": 1,
      "name": "Чистка обуви",
      "description": "Профессиональная чистка обуви",
      "price": "1000.00"
    },
    "status": "pending",
    "created_at": "2024-12-10T12:00:00Z",
    "street": "Ленина",
    "building_num": "1",
    "apartment": "42",
    "comment": "Позвоните за час до приезда"
  }
]
```

#### Создание нового заказа

```http
POST /api/orders/client/orders/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**

```json
{
  "service": 1,
  "street": "Ленина",
  "building_num": "1",
  "apartment": "42",
  "comment": "Позвоните за час до приезда"
}
```

### Эндпоинты для курьеров

#### Получение доступных заказов

```http
GET /api/orders/courier/orders/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "service": {
      "id": 1,
      "name": "Чистка обуви",
      "description": "Профессиональная чистка обуви",
      "price": "1000.00"
    },
    "status": "pending",
    "customer": {
      "id": 1,
      "first_name": "Иван",
      "last_name": "Иванов"
    },
    "street": "Ленина",
    "building_num": "1",
    "apartment": "42"
  }
]
```

#### Получение назначенных заказов

```http
GET /api/orders/courier/orders/assigned_orders/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Получение завершенных заказов

```http
GET /api/orders/courier/orders/completed_orders/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Принятие заказа курьером

```http
PATCH /api/orders/courier/orders/{order_id}/assign/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Отмена принятия заказа

```http
PATCH /api/orders/courier/orders/{order_id}/unassign/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Обновление статуса заказа

```http
PATCH /api/orders/courier/orders/{order_id}/update_status/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**

```json
{
  "status": "courier_on_the_way"
}
```

**Возможные статусы заказа:**

- `pending` - Ожидает курьера
- `courier_assigned` - Курьер назначен
- `courier_on_the_way` - Курьер в пути
- `at_location` - На месте выполнения
- `courier_on_the_way_to_master` - Курьер в пути к мастеру
- `in_progress` - В работе у мастера
- `completed` - Завершен
- `cancelled` - Отменен
- `return` - Возврат

### Использование на фронтенде (React + TypeScript пример)

```typescript
// types.ts
interface Order {
  id: number;
  service: {
    id: number;
    name: string;
    description: string;
    price: string;
  };
  status: string;
  created_at: string;
  street: string;
  building_num: string;
  apartment: string;
  comment?: string;
}

// api.ts
const API_BASE_URL = "http://localhost:8000/api";

export const ordersApi = {
  // Для клиентов
  async getClientOrders(): Promise<Order[]> {
    const response = await fetch(`${API_BASE_URL}/orders/client/orders/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.json();
  },

  async createOrder(orderData: Partial<Order>): Promise<Order> {
    const response = await fetch(`${API_BASE_URL}/orders/client/orders/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(orderData),
    });
    return response.json();
  },

  // Для курьеров
  async getAvailableOrders(): Promise<Order[]> {
    const response = await fetch(`${API_BASE_URL}/orders/courier/orders/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });
    return response.json();
  },

  async getAssignedOrders(): Promise<Order[]> {
    const response = await fetch(
      `${API_BASE_URL}/orders/courier/orders/assigned_orders/`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      }
    );
    return response.json();
  },

  async assignOrder(orderId: number): Promise<Order> {
    const response = await fetch(
      `${API_BASE_URL}/orders/courier/orders/${orderId}/assign/`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      }
    );
    return response.json();
  },

  async updateOrderStatus(orderId: number, status: string): Promise<Order> {
    const response = await fetch(
      `${API_BASE_URL}/orders/courier/orders/${orderId}/update_status/`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status }),
      }
    );
    return response.json();
  },
};

// Пример использования в React компоненте
function OrdersList() {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    // Для клиента
    ordersApi.getClientOrders().then(setOrders);
    // Или для курьера
    // ordersApi.getAvailableOrders().then(setOrders);
  }, []);

  return (
    <div>
      {orders.map((order) => (
        <div key={order.id}>
          <h3>Заказ #{order.id}</h3>
          <p>Услуга: {order.service.name}</p>
          <p>Статус: {order.status}</p>
          <p>
            Адрес: {order.street}, {order.building_num}
          </p>
        </div>
      ))}
    </div>
  );
}
```

### Обработка WebSocket уведомлений

```typescript
// notifications.ts
class NotificationService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect() {
    const token = localStorage.getItem("token");
    this.ws = new WebSocket(
      `ws://localhost:8000/ws/notifications/?token=${token}`
    );

    this.ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      // Обработка уведомления (например, показ toast сообщения)
      console.log("Получено уведомление:", notification);
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, 3000);
      }
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const notificationService = new NotificationService();

// Использование в React приложении
useEffect(() => {
  notificationService.connect();
  return () => notificationService.disconnect();
}, []);
```

### Обработка ошибок

Все запросы должны включать обработку ошибок:

```typescript
try {
  const orders = await ordersApi.getClientOrders();
  setOrders(orders);
} catch (error) {
  if (error.response?.status === 401) {
    // Неавторизован - перенаправить на страницу вхо��а
    navigate("/login");
  } else {
    // Показать сообщение об ошибке
    showErrorMessage("Не удалось загрузить заказы");
  }
}
```

### Важные замечания

1. Все запросы требуют валидный JWT токен в заголовке Authorization
2. Для работы с заказами пользователь должен иметь соответствующую роль (client или courier)
3. WebSocket соединение автоматически переподключается при разрыве связи
4. Статусы заказов меняются последовательно, нельзя пропускать промежуточные статусы
5. При обновлении статуса заказа автоматически отправляются уведомления всем заинтересованным сторонам

# Система уведомлений

## WebSocket соединение

### Подключение к WebSocket

```typescript
const connectToWebSocket = (token: string) => {
  const ws = new WebSocket(
    `ws://localhost:8000/ws/notifications/?token=${token}`
  );

  ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    // Обработк�� уведомления
  };

  ws.onclose = () => {
    // Переподключение через 5 секунд
    setTimeout(connectToWebSocket, 5000);
  };

  return ws;
};
```

### Формат уведомлений

Все уведомления имеют следующую структуру:

```typescript
interface Notification {
  id: number;
  type: NotificationType;
  title: string;
  message: string;
  order_id?: number;
  order_status?: OrderStatus;
  created_at: string;
  is_read: boolean;
}

type NotificationType =
  | "new_order" // Новый заказ (для курьеров)
  | "courier_assigned" // Курьер назначен (для клиента)
  | "courier_on_the_way" // Курьер в пути (для клиента)
  | "at_location" // Курьер на месте (для клиента)
  | "courier_on_the_way_to_master" // Курьер везет заказ мастеру (для клиента)
  | "in_progress" // Заказ в работе у мастера (для клиента)
  | "completed" // Заказ выполнен (для клиента)
  | "cancelled" // Заказ отменен
  | "return" // Возврат заказа
  | "system"; // Системное уведомление

type OrderStatus =
  | "pending"
  | "courier_assigned"
  | "courier_on_the_way"
  | "at_location"
  | "courier_on_the_way_to_master"
  | "in_progress"
  | "completed"
  | "cancelled"
  | "return";
```

### Пример обработки уведомлений

```typescript
const handleNotification = (notification: Notification) => {
  switch (notification.type) {
    case "new_order":
      // Для курьеров: показать новый доступный заказ
      showNewOrderNotification(notification);
      break;

    case "courier_assigned":
      // Для клиента: показать информацию о назначенном курьере
      showCourierAssignedNotification(notification);
      break;

    case "courier_on_the_way":
    case "at_location":
    case "courier_on_the_way_to_master":
    case "in_progress":
    case "completed":
      // Обновить статус заказа в интерфейсе
      updateOrderStatus(notification.order_id, notification.order_status);
      // Показать уведомление
      showStatusUpdateNotification(notification);
      break;

    case "cancelled":
    case "return":
      // Показать важное уведомление об отмене/возврате
      showImportantNotification(notification);
      break;

    case "system":
      // Показать системное уведомление
      showSystemNotification(notification);
      break;
  }
};
```

## REST API для уведомлений

### Получение списка уведомлений

```http
GET /api/notifications/
```

**Headers:**

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "type": "new_order",
    "title": "Новый заказ",
    "message": "Доступен новый заказ на чистку обуви",
    "order": {
      "id": 1,
      "service": {
        "id": 1,
        "name": "Чистка обуви"
      },
      "status": "pending",
      "created_at": "2024-12-10T12:00:00Z"
    },
    "created_at": "2024-12-10T12:00:00Z",
    "is_read": false
  }
]
```

### Получение непрочитанных уведомлений

```http
GET /api/notifications/unread/
```

### Отметка уведомления как прочитанного

```http
POST /api/notifications/{id}/mark_as_read/
```

### Отметка всех уведомлений как прочитанных

```http
POST /api/notifications/mark_all_as_read/
```

## Примеры использования

### Ком��онент NotificationProvider

```typescript
import React, { useEffect, useContext, createContext } from "react";

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType>(null!);

export const NotificationProvider: React.FC = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) return;

    // Загрузка существующих уведомлений
    fetchNotifications();

    // Подключение к WebSocket
    const websocket = connectToWebSocket(token);
    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [token]);

  const fetchNotifications = async () => {
    try {
      const response = await fetch("/api/notifications/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setNotifications(data);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await fetch(`/api/notifications/${id}/mark_as_read/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setNotifications(
        notifications.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch("/api/notifications/mark_all_as_read/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
    }
  };

  const value = {
    notifications,
    unreadCount: notifications.filter((n) => !n.is_read).length,
    markAsRead,
    markAllAsRead,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Hook для использования уведомлений
export const useNotifications = () => {
  return useContext(NotificationContext);
};
```

### Использование в компонентах

```typescript
// Компонент NotificationBell
const NotificationBell: React.FC = () => {
  const { unreadCount } = useNotifications();

  return (
    <div className="notification-bell">
      <IconBell />
      {unreadCount > 0 && (
        <span className="notification-badge">{unreadCount}</span>
      )}
    </div>
  );
};

// Компонент NotificationList
const NotificationList: React.FC = () => {
  const { notifications, markAsRead, markAllAsRead } = useNotifications();

  return (
    <div className="notifications-list">
      <div className="notifications-header">
        <h3>Уведомления</h3>
        <button onClick={markAllAsRead}>Отметить все как прочитанные</button>
      </div>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification-item ${
            !notification.is_read ? "unread" : ""
          }`}
          onClick={() => markAsRead(notification.id)}
        >
          <div className="notification-title">{notification.title}</div>
          <div className="notification-message">{notification.message}</div>
          <div className="notification-time">
            {new Date(notification.created_at).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
};
```

## Важные замечания

1. **Обработка переподключения WebSocket:**

   - Реализовано автоматическое переподключение при разрыве соединения
   - Максимальное количество попыток переподключения настраивается
   - При отсутствии соединения уведомления все равно доступны через REST API

2. **Типы уведомлений:**

   - Каждый тип уведомления соответствует определенному статусу заказа
   - Системные уведомления используются для служебных сообщений
   - Все уведомления сохраняются в базе данных

3. **Безопасность:**

   - Все запросы требуют валидный JWT токен
   - WebSocket соединение также аутентифицируется через токен
   - Пользователь получает только свои уведомления

4. **Производительность:**

   - Уведомления отправляются только целевым пользователям
   - Фильтрация происходит на уровне базы данных
   - WebSocket соединение поддерживает автоматическое переподключение

5. **Обработка ошибок:**
   - Автоматическое обновление токена при истечении срока действия
   - Автоматическое переподключение WebSocket при разрыве соединения
   - Сохранение уведомлений в базе данных для надежности
   - Логи��ование ошибок для отладки

## Решенные проблемы и их исправление

### Проблема с аутентификацией (10.12.2023)

#### Описание проблемы

В системе возникла проблема с доступом к админ-панели Django и общей аутентификацией. Проблема была вызвана избыточными механизмами безопасности, которые были добавлены в систему:

1. Проверка IP-адреса в JWT токенах
2. Дополнительный middleware для проверки IP

#### Симптомы

- Невозможность входа в админ-панель Django
- Частые автоматические выходы из системы
- Проблемы с аутентификацией при смене сети

#### Причина

Основной причиной стало добавление следующих компонентов:

```python
# В настройках SIMPLE_JWT:
'AUTH_TOKEN_EXTEND_CLAIMS': {
    'ip_address': lambda request: request.META.get('REMOTE_ADDR'),
}

# В MIDDLEWARE:
'authentication.middleware.IPAwareJWTAuthenticationMiddleware'
```

Эти компоненты создав��ли жесткую привязку токенов к IP-адресу пользователя, что приводило к проблемам при:

- Смене сети (WiFi -> мобильный интернет)
- Использовании прокси или VPN
- Динамических IP-адресах

#### Решение

1. Удалена проверка IP-адреса из настроек JWT
2. Убран дополнительный middleware
3. Сохранены все основные механизмы безопасности:
   - Стандартная JWT аутентификация
   - Blacklist для отозванных токенов
   - Ротация refresh токенов
   - Все permissions и ограничения доступа

#### Влияние на безопасность

- Система осталась защищенной благодаря стандартным механизмам JWT
- Убрана только избыточная проверка IP, которая создавала проблемы
- Все остальные механизмы безопасности работают как прежде

#### Влияние на пользователей

- Улучшена стабильность аутентификации
- Устранены проб��емы при смене сети
- Сохранен весь функционал системы
