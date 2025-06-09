"""
Validadores personalizados de contraseñas para CaosNewsApp
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexPasswordValidator:
    """
    Valida que la contraseña contenga al menos:
    - 1 mayúscula
    - 1 minúscula
    - 1 número
    - 1 símbolo especial
    """

    def validate(self, password, user=None):
        errors = []

        # Verificar mayúscula
        if not re.search(r'[A-Z]', password):
            errors.append(_("La contraseña debe contener al menos una letra mayúscula."))

        # Verificar minúscula
        if not re.search(r'[a-z]', password):
            errors.append(_("La contraseña debe contener al menos una letra minúscula."))

        # Verificar número
        if not re.search(r'\d', password):
            errors.append(_("La contraseña debe contener al menos un número."))

        # Verificar símbolo especial
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append(_("La contraseña debe contener al menos un símbolo especial (!@#$%^&*)."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Su contraseña debe contener al menos una letra mayúscula, "
            "una minúscula, un número y un símbolo especial (!@#$%^&*)."
        )


class MinimumLengthValidator:
    """
    Validador personalizado para longitud mínima con mensaje en español
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("La contraseña debe tener al menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Su contraseña debe contener al menos %(min_length)d caracteres."
        ) % {'min_length': self.min_length}
