from django.db import models
from django.utils.text import slugify

# Модель услуги
class Service(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='services/icons/%Y/%m', blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(null=False, unique=True, blank=True)

    class Meta:
        verbose_name = 'Услуга'  # Отображаемое название модели в единственном числе
        verbose_name_plural = 'Услуги'  # Отображаемое название модели во множественном числе

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)    



    def __str__(self):
        return self.name

# Модель атрибута (например, "Цвет")
class Attribute(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Атрибут'  # Отображаемое название модели в единственном числе
        verbose_name_plural = 'Атрибуты'  # Отображаемое название модели во множественном числе

    def __str__(self):
        return self.name

# Промежуточная модель для связывания услуги и атрибута, а также для хранения значения атрибута
class ServiceAttribute(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)  # Значение атрибута (например, "Красный")

    def __str__(self):
        return f"{self.attribute.name}: {self.value} for {self.service.name}"

# Модель опции (например, "Размер")
class Option(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Опция'  # Отображаемое название модели в единственном числе
        verbose_name_plural = 'Опции'  # Отображаемое название модели во множественном числе

    def __str__(self):
        return self.name

# Промежуточная модель для связывания услуги и опции
class ServiceOption(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)  # Значение опции (например, "Large")

    def __str__(self):
        return f"{self.option.name}: {self.value} for {self.service.name}"

