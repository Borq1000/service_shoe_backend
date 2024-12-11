from rest_framework import serializers
from .models import Order
from service.models import Service
from authentication.models import User


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order.
    """
    customer = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    courier = serializers.PrimaryKeyRelatedField(
        read_only=True,
        allow_null=True,
    )
    service_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'service', 'service_details', 'customer', 'city', 'street', 'building_num',
            'building', 'floor', 'apartment', 'latitude', 'longitude', 'courier',
            'status', 'status_changed_at', 'created_at', 'comment', 'image', 'price'
        ]
        extra_kwargs = {
            'image': {'required': False},
            'latitude': {'required': False},
            'longitude': {'required': False},
            'status': {'read_only': True},  # Ограничиваем возможность изменять статус через сериализатор
            'price': {'read_only': True},   # Цена вычисляется на основе услуги
        }

    def get_service_details(self, obj):
        """
        Возвращает детализированную информацию об услуге.
        """
        return {
            'name': obj.service.name,
            'description': obj.service.description,
            'price': obj.service.price
        }

    def validate_image(self, value):
        """
        Валидация изображения (опционально).
        """
        return value

    def create(self, validated_data):
        """
        Создание заказа для клиента с автоматическим присвоением customer.
        """
        user = self.context['request'].user
        if user.user_type != 'client':
            raise serializers.ValidationError("Only clients can create orders.")
        validated_data['customer'] = user
        return super().create(validated_data)
