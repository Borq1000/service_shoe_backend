from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ServiceViewSet, AttributeViewSet, OptionViewSet

router = SimpleRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'attributes', AttributeViewSet)
router.register(r'options', OptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
