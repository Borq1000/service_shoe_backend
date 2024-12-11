from rest_framework import viewsets
from .models import Service, Attribute, Option
from .serializers import ServiceSerializer, AttributeSerializer, OptionSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'slug'

    def get_object(self):
        # Метод get_object уже корректно обрабатывает slug благодаря настройке lookup_field
        return super().get_object()

    

class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer