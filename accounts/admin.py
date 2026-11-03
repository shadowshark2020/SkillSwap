from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# 1. Importa tu modelo de usuario (cambia 'User' si en models.py se llama distinto, como 'CustomUser')
from .models import TeacherProfile, User 

# 2. Registra el modelo principal para que aparezca en el panel
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass # Esto aplica la vista profesional completa que Django trae por defecto

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'verification_request_status', 'has_document')
    list_filter = ('is_verified', 'verification_request_status')
    search_fields = ('user__email', 'user__username')
    actions = ['approve_and_delete_docs', 'reject_verification']

    def has_document(self, obj):
        return bool(obj.verification_document)
    has_document.boolean = True
    has_document.short_description = "Tiene PDF"

    @admin.action(description="Aprobar verificación y BORRAR PDF (Privacidad)")
    def approve_and_delete_docs(self, request, queryset):
        for profile in queryset:
            profile.is_verified = True
            profile.verification_request_status = 'approved'
            if profile.verification_document:
                profile.verification_document.delete(save=False)
            profile.save()
        self.message_user(request, "Selección aprobada y documentos PDF eliminados exitosamente del sistema.")

    @admin.action(description="Rechazar solicitud de verificación")
    def reject_verification(self, request, queryset):
        queryset.update(verification_request_status='rejected', is_verified=False)
        self.message_user(request, "Las solicitudes seleccionadas fueron rechazadas.")