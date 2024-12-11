from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'order', 'created_at', 'is_read']
        read_only_fields = ['recipient']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.order:
            data['order'] = {
                'id': instance.order.id,
                'service': {
                    'id': instance.order.service.id,
                    'name': instance.order.service.name
                },
                'status': instance.order.status,
                'created_at': instance.order.created_at
            }
        return data 