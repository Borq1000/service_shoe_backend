from rest_framework import status, views
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, UserProfileSerializer

from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated


from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch_image(self, request):
        user = request.user
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Файл изображения не предоставлен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']
        
        # Проверка размера файла (5MB)
        if image.size > settings.MAX_IMAGE_SIZE:
            return Response(
                {'error': 'Размер изображения не должен превышать 5MB'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка формата файла
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            return Response(
                {'error': 'Неверный формат изображения. Разрешенные форматы: JPEG, JPG, PNG, GIF, WebP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаление старого изображения, если оно существует
        if user.image:
            user.image.delete(save=False)

        # Сохранение нового изображения
        user.image = image
        user.save()

        return Response({
            'image': request.build_absolute_uri(user.image.url)
        })


class PasswordResetRequestView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"

        send_mail(
            'Password Reset',
            f'Please reset your password by clicking on the following link: {reset_url}',
            'rodopi1000@gmail.com',
            [user.email],
            fail_silently=False,
        )
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)



class UserRegistrationView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            user = request.user
            image = request.FILES.get('image')
            
            if not image:
                return Response(
                    {'error': 'No image provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Обновляем изображение профиля пользователя
            user.profile.image = image  # предполагая, что у вас есть связанная модель Profile
            user.profile.save()

            return Response(
                {'message': 'Profile image updated successfully'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )