from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("registro/", views.register, name="register"),
    path("ingresar/", views.login_view, name="login"),
    path("salir/", views.logout_view, name="logout"),
    path("perfil/editar/", views.edit_profile, name="edit_profile"),
    path('editar-cv/', views.edit_teacher_cv, name='edit_teacher_cv'),
    path('perfil/', views.profile_view, name='profile_view'),
]