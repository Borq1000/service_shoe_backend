from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

class IPAwareJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self._get_user(request))
        return self.get_response(request)

    def _get_user(self, request):
        user = AnonymousUser()
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                validated_token = self.jwt_auth.get_validated_token(auth_header[7:])
                
                # Проверяем IP-адрес, если он был сохранен в токене
                token_ip = validated_token.get('ip_address')
                current_ip = request.META.get('REMOTE_ADDR')
                
                if token_ip and token_ip != current_ip:
                    raise InvalidToken('IP address mismatch')
                
                user = self.jwt_auth.get_user(validated_token)
        except Exception:
            pass
        return user 