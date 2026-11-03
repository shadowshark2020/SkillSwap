from django import forms
from .models import Skill

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["category", "title", "description", "price_per_hour"]
        labels = {
            "category": "Categoría",
            "title": "Título de la clase",
            "description": "Descripción de lo que enseñarás",
            "price_per_hour": "Precio por hora (SkillCoins)",
        }
        widgets = {
            "category": forms.Select(attrs={"class": "form-select rounded-3"}),
            "title": forms.TextInput(attrs={"class": "form-control rounded-3", "placeholder": "Ej. Excel avanzado para negocios"}),
            "description": forms.Textarea(attrs={"class": "form-control rounded-3", "rows": 4, "placeholder": "Detalla qué aprenderá el alumno..."}),
            "price_per_hour": forms.NumberInput(attrs={"class": "form-control rounded-3", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Selecciona una opción"