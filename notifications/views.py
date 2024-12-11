from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает уведомления, фильтруя их по роли пользователя.
        """
        user = self.request.user
        allowed_types = Notification.get_allowed_types_for_user(user)
        return Notification.objects.filter(
            recipient=user,
            type__in=allowed_types
        )

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Отмечает все уведомления пользователя как прочитанные.
        """
        self.get_queryset().update(is_read=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Отмечает конкретное уведомление как прочитанное.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Возвращает непрочитанные уведомления пользователя.
        """
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
