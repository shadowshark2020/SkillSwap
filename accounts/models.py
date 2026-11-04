import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ALUMNO = "alumno", "Alumno"
        MAESTRO = "maestro", "Maestro"
        ADMIN = "admin", "Administrador"

    email = models.EmailField("correo electrónico", unique=True)
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.ALUMNO
    )
    bio = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def clean(self):
        super().clean()
        # Regla estricta: No se puede cambiar el rol una vez creado
        if self.pk:
            old_user = User.objects.get(pk=self.pk)
            if old_user.role != self.role:
                raise ValidationError("El rol es permanente y no puede ser modificado tras el registro.")

    def _generate_username(self):
        """Crea un username único a partir del correo (parte antes de la @)."""
        max_len = self._meta.get_field("username").max_length
        base = (self.email or "usuario").split("@")[0]
        base = re.sub(r"[^\w.@+-]", "", base)[: max_len - 6] or "usuario"

        candidate = base
        counter = 1
        while User.objects.filter(username=candidate).exclude(pk=self.pk).exists():
            counter += 1
            candidate = f"{base}{counter}"
        return candidate

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN

        # Si no se indicó username, se genera antes de validar
        if not self.username:
            self.username = self._generate_username()

        # Ejecuta clean() automáticamente al guardar para aplicar la validación
        self.full_clean(exclude=['password'])
        super().save(*args, **kwargs)

    @property
    def has_profile(self) -> bool:
        """Verifica si el maestro ya completó su CV."""
        return TeacherProfile.objects.filter(user=self).exists()


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    experience = models.TextField("Experiencia", blank=True, null=True)
    bio = models.TextField("Biografía Profesional", blank=True, null=True)

    is_verified = models.BooleanField("Verificado", default=False)
    verification_request_status = models.CharField(max_length=20, default='none')

    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.email}"