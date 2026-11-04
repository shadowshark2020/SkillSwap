from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import TeacherProfile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    ROLES_PERMITIDOS = [
        ('alumno', 'Alumno'),
        ('maestro', 'Maestro'),
    ]
    
    # Cambiamos "Role" por "Tipo de usuario"
    role = forms.ChoiceField(choices=ROLES_PERMITIDOS, label="Tipo de usuario")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iterar sobre los campos para darles estilo y arreglar el texto final
        for field_name, field in self.fields.items():
            
            # Aplicar clases de Bootstrap y nuestra clase personalizada 'ss-input'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select ss-input text-white'})
            else:
                field.widget.attrs.update({'class': 'form-control ss-input text-white'})
            
            # Cambiar "Contraseña (confirmación)" por "Repetir contraseña"
            if field.label and 'confirm' in str(field.label).lower():
                field.label = "Repetir contraseña"

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['experience', 'bio', 'verification_document']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }