from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied

from .forms import CustomUserCreationForm, TeacherProfileForm
from .models import TeacherProfile
from wallet.models import Wallet 


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Obtiene el monedero o lo crea, y asigna las 20 monedas de bono
            wallet, created = Wallet.objects.get_or_create(user=user)
            if created or wallet.balance == 0:
                wallet.balance = 20
                wallet.save()
            
            login(request, user)
            
            if user.role == user.Role.MAESTRO:
                return redirect("accounts:edit_profile")
            return redirect("marketplace:explore")
    else:
        form = CustomUserCreationForm()
        
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("marketplace:explore")
    else:
        form = AuthenticationForm()
        
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


# ==========================================
# EDICIÓN DE PERFIL GENERAL (Para Todos)
# ==========================================
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        
        if hasattr(user, 'bio'):
            user.bio = request.POST.get('bio', user.bio)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        messages.success(request, "¡Perfil actualizado con éxito!")
        return redirect('accounts:edit_profile')

    return render(request, 'accounts/edit_profile.html')


# ==========================================
# HOJA DE VIDA / PERFIL PROFESIONAL (Solo Maestros)
# ==========================================
@login_required
def edit_teacher_cv(request):
    if request.user.role != request.user.Role.MAESTRO:
        raise PermissionDenied("Solo los maestros pueden tener un perfil profesional o hoja de vida.")
    
    profile, created = TeacherProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Hoja de vida actualizada con éxito!")
            return redirect("accounts:edit_teacher_cv")
    else:
        form = TeacherProfileForm(instance=profile)
        
    return render(request, "accounts/edit_teacher_cv.html", {"form": form})

@login_required
def profile_view(request):
    teacher_profile = None
    if request.user.role == request.user.Role.MAESTRO:
        teacher_profile = TeacherProfile.objects.filter(user=request.user).first()
        
    return render(request, "accounts/profile.html", {"teacher_profile": teacher_profile})

@login_required
def request_verification(request):
    if request.user.role != request.user.Role.MAESTRO:
        messages.error(request, "Solo los maestros pueden solicitar verificación.")
        return redirect("marketplace:explore")
        
    profile, created = TeacherProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        profile.verification_request_status = 'pending'
        profile.save()
        messages.success(request, "¡Solicitud de verificación enviada al equipo de administración!")
        return redirect("accounts:edit_teacher_cv")
        
    return redirect("accounts:edit_teacher_cv")