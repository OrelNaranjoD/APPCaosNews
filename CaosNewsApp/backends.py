"""
Backends de autenticación personalizados para CaosNews
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend de autenticación que permite login con email o username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')

        if username is None or password is None:
            return None

        User = get_user_model()

        try:
            # Buscar usuario por email o username
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # No existe el usuario
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios, usar el primero encontrado
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
            if not user:
                return None

        # Verificar la contraseña
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Obtener usuario por ID
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
