from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    UserRegistrationView, UserProfileView, UserProfileImageView,
    PasswordResetRequestView, PasswordResetView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<uidb64>/<token>/', PasswordResetView.as_view(), name='reset-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/image/', UserProfileImageView.as_view(), name='user-profile-image'),
]