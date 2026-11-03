from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "marketplace"

urlpatterns = [
    # ==========================================
    # VISTAS PRINCIPALES Y CATÁLOGO
    # ==========================================
    path("explorar/", views.explore, name="explore"),
    path("publicar/", views.create_skill, name="create_skill"),
    path("clase/<int:pk>/", views.skill_detail, name="skill_detail"),
    path("mis-clases/", views.my_skills, name="my_skills"),
    path("mis-clases/eliminar/<int:pk>/", views.delete_skill, name="delete_skill"),
    path("panel/", views.dashboard, name="dashboard"),
    path("como-funciona/", views.how_it_works, name="how_it_works"),
    path("maestro/<int:teacher_id>/perfil/", views.teacher_profile_view, name="teacher_profile"),

    # ==========================================
    # FLUJO DE SOLICITUDES Y CLASES
    # ==========================================
    path("clase/<int:pk>/solicitar/", views.request_class, name="request_class"),
    path("clase/<int:request_id>/completar/", views.complete_class, name="complete_class"),
    path("clase/<int:request_id>/reseña/", views.add_review, name="add_review"),
    path("solicitud/<int:pk>/cancelar/", views.cancel_request, name="cancel_request"),
    path("solicitud/<int:pk>/aceptar/", views.accept_request, name="accept_request"),
    path("solicitud/<int:pk>/rechazar/", views.reject_request, name="reject_request"),

    # ==========================================
    # SISTEMA DE CHAT / INBOX Y NOTIFICACIONES
    # ==========================================
    path("inbox/", views.inbox_view, name="inbox"),
    path("inbox/<int:room_id>/", views.inbox_view, name="inbox_room"),
    path("inbox/<int:room_id>/autorizar-video/", views.authorize_video, name="authorize_video"),
    path("mensaje/anular/<int:message_id>/", views.delete_message, name="delete_message"),
    path("notificaciones/leer/", views.mark_notifications_read, name="mark_notifications_read"),

    # ==========================================
    # SOPORTE Y ASISTENTE VIRTUAL
    # ==========================================
    path("soporte/", views.support_tickets_view, name="support_tickets"),
    path("asistente/", views.assistant_bot_view, name="assistant_bot"),

    # ==========================================
    # SEGURIDAD Y MODERACIÓN
    # ==========================================
    path("usuario/bloquear/<int:user_id>/", views.block_user, name="block_user"),
    path("usuario/reportar/<int:user_id>/", views.report_user, name="report_user"),

    # ==========================================
    # ACCIONES DE ADMINISTRACIÓN (PANEL DE CONTROL)
    # ==========================================
    path("admin-action/aprobar-maestro/<int:profile_id>/", views.admin_approve_teacher, name="admin_approve_teacher"),
    path("admin-action/resolver-ticket/<int:ticket_id>/", views.admin_resolve_ticket, name="admin_resolve_ticket"),

    # ==========================================
    # RECUPERACIÓN DE CONTRASEÑA (DJANGO AUTH)
    # ==========================================
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    
    # ==========================================
    # MISIONES Y RECOMPENSAS
    # ==========================================
    path("misiones/", views.missions_hub, name="missions_hub"),
    path("misiones/reclamar/<int:mission_id>/", views.claim_mission, name="claim_mission"),
]