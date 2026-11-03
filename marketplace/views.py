from django.db import models, transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
import random
import re

from .forms import SkillForm
from .models import (
    Skill, Category, ClassRequest, ChatRoom, Message, 
    Report, Block, SupportTicket, Notification, Review,
    MissionTemplate, UserMission
)
from wallet.models import Wallet

User = get_user_model()

# ==========================================
# 1. UTILIDADES Y BOT DE MODERACIÓN
# ==========================================
FORBIDDEN_WORDS = [
    "puta", "puto", "mierda", "carajo", "pendejo", "pendeja", 
    "cabrón", "cabron", "imbécil", "imbecil", "estúpido", "estupido", 
    "idiota", "estiercol", "gilipollas", "maricón", "maricon", 
    "culero", "chingada", "chingar", "chingado", "verga", "pito", 
    "coño", "huevón", "huevon", "boludo", "pelotudo", "cagada", 
    "cagar", "mamón", "mamon", "zorrra", "zorra", "chupada",
    "tarado", "estupidez"
]

def bot_check_content(text):
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(r'\b' + word + r'\b', text_lower):
            return True
    return False

# ==========================================
# 2. VISTAS DE EXPLORACIÓN Y CLASES
# ==========================================
def explore(request):
    skills = Skill.objects.filter(is_active=True).order_by("-created_at")
    categories = Category.objects.all()
    
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    
    if query:
        skills = skills.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        skills = skills.filter(category_id=category_id)
        
    return render(request, "marketplace/explore.html", {
        "skills": skills, 
        "categories": categories, 
        "query": query
    })

def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    return render(request, "marketplace/skill_detail.html", {"skill": skill})

@login_required
def create_skill(request):
    if request.user.role != request.user.Role.MAESTRO:
        raise PermissionDenied("Solo los maestros pueden publicar clases.")
        
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.teacher = request.user
            skill.save()
            return redirect("marketplace:explore") 
    else:
        form = SkillForm()
        
    return render(request, "marketplace/create_skill.html", {"form": form})

@login_required
def my_skills(request):
    mis_clases = Skill.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, "marketplace/my_skills.html", {"mis_clases": mis_clases})

@login_required
def delete_skill(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.teacher != request.user:
        messages.error(request, "Acceso denegado: No puedes eliminar una clase que no es tuya.")
        return redirect("marketplace:my_skills")
        
    if request.method == "POST":
        skill.delete()
        messages.success(request, f"La clase '{skill.title}' ha sido eliminada.")
        
    return redirect("marketplace:my_skills")

def how_it_works(request):
    return render(request, 'marketplace/how_it_works.html')

# ==========================================
# 3. PANEL DE USUARIO Y PERFIL DE MAESTRO
# ==========================================
@login_required
def dashboard(request):
    mis_compras = ClassRequest.objects.filter(student=request.user).order_by('-created_at')
    mis_ventas = ClassRequest.objects.filter(skill__teacher=request.user).order_by('-created_at')
    
    # Herramientas exclusivas para administradores
    pending_verifications = []
    open_tickets = []
    recent_reports = []
    
    if request.user.is_staff or request.user.is_superuser:
        from accounts.models import TeacherProfile
        pending_verifications = TeacherProfile.objects.filter(verification_request_status='pending')
        open_tickets = SupportTicket.objects.filter(status='open')
        recent_reports = Report.objects.all().order_by('-created_at')[:5]
        
    return render(request, "marketplace/dashboard.html", {
        "mis_compras": mis_compras, 
        "mis_ventas": mis_ventas,
        "pending_verifications": pending_verifications,
        "open_tickets": open_tickets,
        "recent_reports": recent_reports
    })

@login_required
def teacher_profile_view(request, teacher_id):
    teacher = get_object_or_404(User, pk=teacher_id)
    
    if teacher.role != teacher.Role.MAESTRO:
        messages.error(request, "Este usuario no es un maestro.")
        return redirect("marketplace:explore")
        
    from accounts.models import TeacherProfile
    teacher_profile = TeacherProfile.objects.filter(user=teacher).first()
    teacher_skills = Skill.objects.filter(teacher=teacher, is_active=True)
    
    return render(request, "marketplace/teacher_profile.html", {
        "teacher": teacher,
        "teacher_profile": teacher_profile,
        "teacher_skills": teacher_skills
    })

# ==========================================
# 4. FLUJO DE SOLICITUDES Y CLASES
# ==========================================
@login_required
def request_class(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == 'POST':
        if request.user.role.lower() != 'alumno':
            messages.error(request, "Solo los alumnos pueden solicitar clases.")
            return redirect("marketplace:skill_detail", pk=pk)
            
        with transaction.atomic():
            wallet = request.user.wallet
            if wallet.balance < skill.price_per_hour:
                messages.error(request, "No tienes suficientes SkillCoins.")
                return redirect("marketplace:skill_detail", pk=pk)
                
            ClassRequest.objects.create(student=request.user, skill=skill, status='pending')
            
            Notification.objects.create(
                recipient=skill.teacher, 
                sender=request.user,
                message=f"solicitó tu clase '{skill.title}'.", 
                link="/marketplace/panel/"
            )
            
            messages.success(request, f"¡Has solicitado la clase '{skill.title}' con éxito!")
            return redirect("marketplace:dashboard")
    return redirect("marketplace:skill_detail", pk=pk)

@login_required
def cancel_request(request, pk):
    class_req = get_object_or_404(ClassRequest, pk=pk)
    if class_req.student == request.user and class_req.status == 'pending':
        class_req.status = 'cancelled'
        class_req.save()
        
        Notification.objects.create(
            recipient=class_req.skill.teacher, 
            sender=request.user, 
            message=f"canceló la solicitud de '{class_req.skill.title}'.", 
            link="/marketplace/panel/"
        )
        
        messages.info(request, "Has cancelado la solicitud.")
    return redirect("marketplace:dashboard")

@login_required
def accept_request(request, pk):
    class_req = get_object_or_404(ClassRequest, pk=pk)
    if class_req.skill.teacher == request.user and class_req.status == 'pending':
        class_req.status = 'accepted'
        class_req.save()
        
        chat_room, created = ChatRoom.objects.get_or_create(class_request=class_req)
        
        Notification.objects.create(
            recipient=class_req.student, 
            sender=request.user,
            message=f"aceptó tu solicitud para '{class_req.skill.title}'.", 
            link=f"/marketplace/inbox/{chat_room.id}/"
        )
        
        messages.success(request, f"Has aceptado la clase.")
        return redirect("marketplace:inbox_room", room_id=chat_room.id)
    return redirect("marketplace:dashboard")

@login_required
def reject_request(request, pk):
    class_req = get_object_or_404(ClassRequest, pk=pk)
    if class_req.skill.teacher == request.user and class_req.status == 'pending':
        class_req.status = 'cancelled'
        class_req.save()
        
        Notification.objects.create(
            recipient=class_req.student, 
            sender=request.user, 
            message=f"rechazó tu solicitud para '{class_req.skill.title}'.", 
            link="/marketplace/panel/"
        )
        
        messages.info(request, "Has rechazado la solicitud.")
    return redirect("marketplace:dashboard")

@login_required
def complete_class(request, request_id):
    class_req = get_object_or_404(ClassRequest, pk=request_id)
    
    if request.user != class_req.student and request.user != class_req.skill.teacher:
        messages.error(request, "No autorizado.")
        return redirect("marketplace:dashboard")
        
    if class_req.status == 'accepted':
        class_req.status = 'completed'
        class_req.save()
        
        # Transferencia automática de SkillCoins al profesor
        student_wallet = Wallet.objects.get(user=class_req.student)
        teacher_wallet, _ = Wallet.objects.get_or_create(user=class_req.skill.teacher)
        
        cost = class_req.skill.price_per_hour
        if student_wallet.balance >= cost:
            student_wallet.balance -= cost
            student_wallet.save()
            
            teacher_wallet.balance += cost
            teacher_wallet.save()
            messages.success(request, f"¡Clase completada! Se transfirieron {cost} SkillCoins al profesor.")
        else:
            messages.warning(request, "La clase se completó, pero el alumno no tenía fondos suficientes para la transferencia.")
            
    if hasattr(class_req, 'chatroom') and class_req.chatroom:
        return redirect('marketplace:inbox_room', room_id=class_req.chatroom.id)
    return redirect('marketplace:dashboard')

@login_required
def add_review(request, request_id):
    class_req = get_object_or_404(ClassRequest, pk=request_id, student=request.user, status='completed')
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        
        Review.objects.get_or_create(
            class_request=class_req,
            defaults={
                'teacher': class_req.skill.teacher,
                'student': request.user,
                'rating': rating,
                'comment': comment
            }
        )
        messages.success(request, "¡Gracias por dejar tu reseña!")
    return redirect('marketplace:dashboard')

# ==========================================
# 5. SISTEMA DE CHAT / INBOX Y NOTIFICACIONES
# ==========================================
@login_required
def inbox_view(request, room_id=None):
    chat_rooms = ChatRoom.objects.filter(
        Q(class_request__student=request.user) | Q(class_request__skill__teacher=request.user)
    ).order_by('-created_at')

    active_room = None
    messages_list = []
    other_user = None
    is_blocked = False

    if room_id:
        active_room = get_object_or_404(ChatRoom, pk=room_id)
        if request.user != active_room.class_request.student and request.user != active_room.class_request.skill.teacher:
            messages.error(request, "No tienes acceso a este chat.")
            return redirect("marketplace:inbox")
        
        class_req = active_room.class_request
        other_user = class_req.skill.teacher if request.user == class_req.student else class_req.student
        
        is_blocked = Block.objects.filter(blocker=other_user, blocked=request.user).exists() or \
                     Block.objects.filter(blocker=request.user, blocked=other_user).exists()

        if request.method == 'POST' and not is_blocked:
            content = request.POST.get('content', '').strip()
            attachment = request.FILES.get('attachment')
            reply_to_id = request.POST.get('reply_to_id')
            
            reply_message = None
            if reply_to_id:
                reply_message = Message.objects.filter(pk=reply_to_id, room=active_room).first()
            
            if content or attachment:
                flagged = False
                if content:
                    flagged = bot_check_content(content)
                    
                Message.objects.create(
                    room=active_room,
                    sender=request.user,
                    content=content,
                    attachment=attachment,
                    is_flagged_by_bot=flagged,
                    reply_to=reply_message
                )
                
                Notification.objects.create(
                    recipient=other_user, 
                    sender=request.user,
                    message="te envió un nuevo mensaje.", 
                    link=f"/marketplace/inbox/{active_room.id}/"
                )
                
                if flagged:
                    messages.warning(request, "Tu mensaje fue moderado.")
                return redirect('marketplace:inbox_room', room_id=active_room.id)

        messages_list = active_room.messages.all().order_by('timestamp')

    return render(request, 'marketplace/inbox.html', {
        'chat_rooms': chat_rooms, 'active_room': active_room,
        'messages_list': messages_list, 'other_user': other_user, 'is_blocked': is_blocked
    })

@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(Message, pk=message_id)
    room_id = msg.room.id
    if msg.sender == request.user:
        msg.delete()
        messages.success(request, "Mensaje anulado.")
    return redirect('marketplace:inbox_room', room_id=room_id)

@login_required
def authorize_video(request, room_id):
    chat_room = get_object_or_404(ChatRoom, pk=room_id)
    if request.user == chat_room.class_request.skill.teacher:
        chat_room.is_video_authorized = not chat_room.is_video_authorized
        chat_room.save()
        messages.success(request, "Estado de video actualizado.")
    return redirect('marketplace:inbox_room', room_id=chat_room.id)

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:dashboard'))

# ==========================================
# 6. SOPORTE Y ASISTENTE VIRTUAL
# ==========================================
@login_required
def assistant_bot_view(request):
    bot_reply = None
    if request.method == 'POST':
        q = request.POST.get('query', '').lower().strip()
        if any(w in q for w in ['skillcoin', 'moneda', 'saldo', 'pagar']):
            bot_reply = "Las SkillCoins son la moneda virtual de SkillSwap para pagar clases."
        elif any(w in q for w in ['clase', 'aprender', 'enseñar']):
            bot_reply = "Explora el catálogo para aprender o publica clases si eres maestro."
        elif any(w in q for w in ['chat', 'mensaje']):
            bot_reply = "Cuando un maestro acepta tu solicitud, se habilita una sala de chat en 'Mensajes'."
        else:
            bot_reply = "Soy el asistente virtual. Si tienes un problema avanzado, crea un Ticket de Soporte."
    return render(request, 'marketplace/assistant_bot.html', {'bot_reply': bot_reply})

@login_required
def support_tickets_view(request):
    if request.method == 'POST':
        SupportTicket.objects.create(
            user=request.user, subject=request.POST.get('subject'), message=request.POST.get('message')
        )
        messages.success(request, "Ticket enviado correctamente.")
        return redirect('marketplace:support_tickets')
    user_tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/support_tickets.html', {'user_tickets': user_tickets})

# ==========================================
# 7. SEGURIDAD Y MODERACIÓN
# ==========================================
@login_required
def block_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user != request.user:
        Block.objects.get_or_create(blocker=request.user, blocked=target_user)
        messages.error(request, "Usuario bloqueado.")
    return redirect('marketplace:dashboard')

@login_required
def report_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Reporte general')
        description = request.POST.get('description', 'Sin descripción')
        Report.objects.create(
            reporter=request.user,
            reported_user=target_user,
            reason=reason,
            description=description
        )
        messages.success(request, "Reporte enviado exitosamente. El equipo de moderación lo revisará.")
        
    return redirect('marketplace:dashboard')

# ==========================================
# 8. ACCIONES DE ADMINISTRACIÓN (DASHBOARD)
# ==========================================
@login_required
def admin_approve_teacher(request, profile_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Acceso no autorizado.")
        return redirect("marketplace:dashboard")
        
    from accounts.models import TeacherProfile
    profile = get_object_or_404(TeacherProfile, pk=profile_id)
    profile.is_verified = True
    profile.verification_request_status = 'approved'
    
    if profile.verification_document:
        profile.verification_document.delete(save=False)
    profile.save()
    
    messages.success(request, f"¡Maestro {profile.user.email} verificado con éxito y PDF eliminado por privacidad!")
    return redirect("marketplace:dashboard")

@login_required
def admin_resolve_ticket(request, ticket_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Acceso no autorizado.")
        return redirect("marketplace:dashboard")
        
    ticket = get_object_or_404(SupportTicket, pk=ticket_id)
    ticket.status = 'resolved'
    ticket.save()
    messages.success(request, f"Ticket #{ticket.id} marcado como resuelto.")
    return redirect("marketplace:dashboard")

# ==========================================
# 9. SISTEMA DE MISIONES Y RECOMPENSAS
# ==========================================
def assign_random_missions(user):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    user_role = user.role.lower() if hasattr(user, 'role') and user.role else 'alumno'
    
    # 1. Diarias (Busca rol del usuario o 'ambos')
    daily_today_count = UserMission.objects.filter(user=user, template__mission_type='daily', assigned_date=today).count()
    if daily_today_count < 5:
        UserMission.objects.filter(user=user, template__mission_type='daily', assigned_date__lt=today, is_claimed=False).delete()
        dailies = list(MissionTemplate.objects.filter(mission_type='daily').filter(Q(target_role='ambos') | Q(target_role=user_role)))
        if dailies:
            count_to_pick = min(5, len(dailies))
            chosen = random.sample(dailies, count_to_pick)
            for m in chosen:
                if not UserMission.objects.filter(user=user, template=m, assigned_date=today).exists():
                    UserMission.objects.create(user=user, template=m, assigned_date=today)

    # 2. Semanales
    weekly_this_week_count = UserMission.objects.filter(user=user, template__mission_type='weekly', assigned_date__gte=start_of_week).count()
    if weekly_this_week_count < 10:
        UserMission.objects.filter(user=user, template__mission_type='weekly', assigned_date__lt=start_of_week, is_claimed=False).delete()
        weeklies = list(MissionTemplate.objects.filter(mission_type='weekly').filter(Q(target_role='ambos') | Q(target_role=user_role)))
        if weeklies:
            count_to_pick = min(10, len(weeklies))
            chosen = random.sample(weeklies, count_to_pick)
            for m in chosen:
                if not UserMission.objects.filter(user=user, template=m, assigned_date__gte=start_of_week).exists():
                    UserMission.objects.create(user=user, template=m, assigned_date=today)

    # 3. Permanentes (Ordenadas)
    permanents_qs = list(MissionTemplate.objects.filter(mission_type='permanent').filter(Q(target_role='ambos') | Q(target_role=user_role)).order_by('id'))
    existing_perms = UserMission.objects.filter(user=user, template__mission_type='permanent').values_list('template_id', flat=True)
    
    new_perms = [m for m in permanents_qs if m.id not in existing_perms]
    if new_perms:
        count_to_add = min(100 - len(existing_perms), len(new_perms))
        if count_to_add > 0:
            for m in new_perms[:count_to_add]:
                UserMission.objects.create(user=user, template=m, assigned_date=today)

@login_required
def missions_hub(request):
    assign_random_missions(request.user)
    
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    daily_missions = UserMission.objects.filter(user=request.user, template__mission_type='daily', assigned_date=today)
    weekly_missions = UserMission.objects.filter(user=request.user, template__mission_type='weekly', assigned_date__gte=start_of_week)
    permanent_missions = UserMission.objects.filter(user=request.user, template__mission_type='permanent')
    
    # Exigir las 5 diarias para el bono
    dailies_completed = daily_missions.filter(is_completed=True).count()
    daily_bonus_claimable = (dailies_completed >= 5)
    
    weekly_has_claimable = weekly_missions.filter(is_completed=True, is_claimed=False).exists()
    
    return render(request, 'marketplace/missions.html', {
        'daily_missions': daily_missions,
        'weekly_missions': weekly_missions,
        'permanent_missions': permanent_missions,
        'dailies_completed': dailies_completed,
        'daily_bonus_claimable': daily_bonus_claimable,
        'weekly_has_claimable': weekly_has_claimable,
    })

@login_required
def claim_mission(request, mission_id):
    mission = get_object_or_404(UserMission, id=mission_id, user=request.user)
    if mission.is_completed and not mission.is_claimed:
        mission.is_claimed = True
        mission.save()
        
        wallet = request.user.wallet
        wallet.balance += mission.template.reward_amount
        wallet.save()
        
        return JsonResponse({'status': 'success', 'reward': mission.template.reward_amount, 'title': mission.template.title})
    return JsonResponse({'status': 'error'})