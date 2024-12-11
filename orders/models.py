from django.db import models
from django.utils import timezone
from service.models import Service
from authentication.models import User



def clean_street_name(street: str, city: str) -> str:
    """
    Удаляет название города, префиксы и лишние символы из названия улицы.
    """
    patterns_to_remove = [f"г {city}", "ул", "пр", "пл", "бул"]
    clean_name = street

    for pattern in patterns_to_remove:
        clean_name = clean_name.replace(f"{pattern},", "").replace(pattern, "").strip()

    # Удаляем пробелы, если они остались после запятой
    clean_name = clean_name.lstrip(",").strip()

    return clean_name

class Order(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_customer')
    city = models.CharField(max_length=100, default="Москва")
    street = models.CharField(max_length=255)  
    building_num = models.CharField(max_length=50, blank=True, null=True)  # Номер дома
    building = models.CharField(max_length=50, blank=True, null=True)  # Корпус
    floor = models.CharField(max_length=50, blank=True, null=True)  # Этаж
    apartment = models.CharField(max_length=50, blank=True, null=True)  # Квартира
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # Широта
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)  # Долгота
    courier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_as_courier')
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('courier_assigned', 'Курьер назначен'),
        ('courier_on_the_way', 'Курьер в пути'),  
        ('at_location', 'На месте выполнения'),
        ('courier_on_the_way_to_master', 'Курьер в пути к мастеру'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),  
        ('return', 'Возврат'),  
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    status_changed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='orders/images/%Y/%m/%d/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    
    def __str__(self):
        return f'Услуга: {self.service.name} - Клиент: {self.customer.first_name} - Дата: {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
    

    def save(self, *args, **kwargs):
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != self.status:
                self.status_changed_at = timezone.now()
        else:
            self.status_changed_at = timezone.now()
        super(Order, self).save(*args, **kwargs)
