from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Order
from .serializers import OrderSerializer
from datetime import timedelta
from django.utils import timezone
from notifications.utils import send_order_notification


class ClientOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заказами клиентов.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if user.user_type != 'client':
            raise PermissionDenied("Only clients can access this endpoint.")
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        # Отправляем уведомление о новом заказе
        send_order_notification(
            order,
            'new_order',
            'Новый заказ',
            f'Появился новый заказ на услугу {order.service.name}'
        )

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        if order.customer != request.user:
            raise PermissionDenied("You do not have permission to view this order.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.customer != request.user:
            raise PermissionDenied("You do not have permission to update this order.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.customer != request.user:
            raise PermissionDenied("You do not have permission to delete this order.")
        return super().destroy(request, *args, **kwargs)


class CourierOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для курьеров для просмотра и управления заказами.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type != 'courier':
            raise PermissionDenied("Only couriers can access this endpoint.")

        if self.action == 'list':
            # Возвращаем заказы, которые досту��ны для принятия
            return Order.objects.filter(status='pending', courier__isnull=True)
        else:
            # Для остальных действий возвращаем все заказы (при необходимости можно ограничить)
            return Order.objects.all()

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        # Проверяем права доступа
        if order.status == 'pending' and order.courier is None:
            pass  # Доступно для всех курьеров
        elif order.courier == user:
            pass  # Заказ назначен текущему курьеру
        else:
            raise PermissionDenied("You do not have permission to view this order.")

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def assigned_orders(self, request):
        """
        Возвращает заказы, назначенные текущему курьеру и не завершенные.
        """
        user = request.user
        orders = Order.objects.filter(courier=user).exclude(status='completed')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed_orders(self, request):
        """
        Возвращает завершённые заказы текущего курьера.
        """
        user = request.user
        orders = Order.objects.filter(courier=user, status='completed')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Назначение курьера к заказу.
        """
        user = request.user
        if user.user_type != 'courier':
            raise PermissionDenied("Only couriers can accept orders.")

        order = self.get_object()
        if order.courier:
            return Response({"detail": "Order is already assigned to a courier."}, status=400)

        if order.status != 'pending':
            return Response({"detail": "Order is not available for assignment."}, status=400)

        order.courier = user
        order.status = 'courier_assigned'
        order.save()

        # Отправляем уведомление клиенту
        send_order_notification(
            order,
            'order_update',
            'Курьер назначен',
            f'Курьер {request.user.first_name} принял ваш заказ'
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def unassign(self, request, pk=None):
        """
        Курьер может отменить назначение заказа.
        """
        user = request.user
        if user.user_type != 'courier':
            raise PermissionDenied("Only couriers can unassign orders.")

        order = self.get_object()
        if order.courier != user:
            return Response({"detail": "You can only unassign orders assigned to you."}, status=400)

        if order.status != 'courier_assigned':
            return Response({"detail": "Order cannot be unassigned in its current status."}, status=400)

        order.courier = None
        order.status = 'pending'
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Курьер может обновить статус заказа.
        """
        user = request.user
        order = self.get_object()

        if user.user_type != 'courier':
            raise PermissionDenied("Only couriers can update the order status.")

        if order.courier != user:
            raise PermissionDenied("You do not have permission to update this order.")

        new_status = request.data.get('status')
        if not new_status:
            return Response({"detail": "Status not provided."}, status=400)

        current_status = order.status

        # Определяем допустимые переходы статусов
        status_flow = {
            'courier_assigned': 'courier_on_the_way',
            'courier_on_the_way': 'at_location',
            'at_location': 'courier_on_the_way_to_master',
            'courier_on_the_way_to_master': 'in_progress',
            'in_progress': 'completed',
        }

        # Определяем допустимые обратные переходы (откаты)
        allowed_previous_status = {
            'courier_on_the_way': 'courier_assigned',
            'at_location': 'courier_on_the_way',
            'courier_on_the_way_to_master': 'at_location',
            'in_progress': 'courier_on_the_way_to_master',
        }

        # Проверя��м, разрешен ли откат статуса
        time_since_change = timezone.now() - order.status_changed_at
        allowed_time = timedelta(minutes=10)

        if new_status == allowed_previous_status.get(current_status):
            if time_since_change <= allowed_time:
                # Разрешаем возврат статуса
                order.status = new_status
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({"detail": "Time to revert status has expired."}, status=400)
        elif status_flow.get(current_status) == new_status:
            old_status = order.status
            order.status = new_status
            order.save()

            # Отправляем уведомление о смене статуса
            status_messages = {
                'courier_on_the_way': 'Курьер выехал к вам',
                'at_location': 'Курьер прибыл на место',
                'courier_on_the_way_to_master': 'Курьер везет обувь мастеру',
                'in_progress': 'Ваш заказ в работе',
                'completed': 'Заказ выполнен'
            }

            if new_status in status_messages:
                send_order_notification(
                    order,
                    'order_update',
                    'Статус заказа изменен',
                    status_messages[new_status]
                )

            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response({"detail": "Invalid status transition."}, status=400)
