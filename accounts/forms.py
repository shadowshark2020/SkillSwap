from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import TeacherProfile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    # 1. Definimos explícitamente solo los roles permitidos
    ROLES_PERMITIDOS = [
        ('alumno', 'Alumno'),
        ('maestro', 'Maestro'),
    ]
    
    # 2. Sobrescribimos el campo role para que solo use las opciones de arriba
    role = forms.ChoiceField(choices=ROLES_PERMITIDOS, label="Role")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role')

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['experience', 'bio', 'verification_document']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }