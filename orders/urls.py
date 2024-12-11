from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientOrderViewSet, CourierOrderViewSet

router = DefaultRouter()
router.register(r'client/orders', ClientOrderViewSet, basename='client-orders')
router.register(r'courier/orders', CourierOrderViewSet, basename='courier-orders')

urlpatterns = [
    path('', include(router.urls)),
]
