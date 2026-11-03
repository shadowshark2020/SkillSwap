import re
from django.core.exceptions import ValidationError


class CustomPasswordValidator:
    def validate(self, password, user=None):
        # 1. Al menos 8 caracteres
        if len(password) < 8:
            raise ValidationError(
                "La contraseña debe tener al menos 8 caracteres.",
                code="password_too_short",
            )

        # 2. Sin espacios
        if " " in password:
            raise ValidationError(
                "La contraseña no debe contener espacios en blanco.",
                code="password_has_spaces",
            )

        # 3. Al menos un número o símbolo
        if not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            raise ValidationError(
                "La contraseña debe contener al menos un número o símbolo.",
                code="password_no_number_or_symbol",
            )

    def get_help_text(self):
        return "La contraseña debe tener al menos 8 caracteres, sin espacios y contener al menos un número o símbolo."