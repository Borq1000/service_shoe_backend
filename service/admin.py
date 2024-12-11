from django.contrib import admin
from .models import Service, Attribute, Option, ServiceAttribute, ServiceOption

class ServiceAttributeInline(admin.TabularInline):
    model = ServiceAttribute
    extra = 1

class ServiceOptionInline(admin.TabularInline):
    model = ServiceOption
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceAttributeInline, ServiceOptionInline]
    list_display = ['name', 'price']
    search_fields = ['name']

admin.site.register(Attribute)
admin.site.register(Option)
