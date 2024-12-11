from django.contrib import admin
from .models import User

admin.site.register(User)

# Изменение заголовка страницы администратора
admin.site.site_header = "Администрирование Shoe Service"
admin.site.site_title = "Shoe Service Админка"
admin.site.index_title = "Добро пожаловать в панель администратора Shoe Service"
