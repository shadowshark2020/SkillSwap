from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=30, default="bi-star")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Skill(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills_taught")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="skills")
    title = models.CharField("título de la clase", max_length=150)
    description = models.TextField("descripción detallada")
    price_per_hour = models.PositiveIntegerField("Costo en SkillCoins por hora", default=10)
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} por {self.teacher.email} ({self.price_per_hour} SC/h)"

class ClassRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests_made")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="requests_received")
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField("Fecha de solicitud", auto_now_add=True)

    def __str__(self):
        return f"Solicitud de {self.student.email} para {self.skill.title}"

class ChatRoom(models.Model):
    class_request = models.OneToOneField(ClassRequest, on_delete=models.CASCADE, related_name="chat_room")
    created_at = models.DateTimeField(auto_now_add=True)
    is_video_authorized = models.BooleanField(default=False)

    def __str__(self):
        return f"Chat para solicitud #{self.class_request.id}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_flagged_by_bot = models.BooleanField(default=False)
    
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='replies')

    def __str__(self):
        return f"Mensaje de {self.sender.email}"

class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_received")
    reason = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Block(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocking")
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Abierto'),
        ('in_progress', 'En Proceso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    subject = models.CharField("Asunto", max_length=200)
    message = models.TextField("Mensaje / Descripción")
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='open')
    admin_response = models.TextField("Respuesta del Administrador", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificación para {self.recipient.email}: {self.message}"

class Review(models.Model):
    class_request = models.OneToOneField(ClassRequest, on_delete=models.CASCADE, related_name='review')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(default=5)  # 1 al 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.student.email} para {self.teacher.email} ({self.rating}★)"

class MissionTemplate(models.Model):
    TYPES = (('daily', 'Diaria'), ('weekly', 'Semanal'), ('permanent', 'Permanente'))
    ROLES = (('alumno', 'Alumno'), ('maestro', 'Maestro'), ('ambos', 'Ambos'))
    
    title = models.CharField(max_length=150)
    description = models.TextField(help_text="Texto que saldrá en la ventana de Info.")
    mission_type = models.CharField(max_length=20, choices=TYPES)
    target_role = models.CharField(max_length=20, choices=ROLES, default='ambos')
    target_count = models.IntegerField(default=1, help_text="Ej: 5 (para 'Juega 5 clases')")
    reward_amount = models.IntegerField(help_text="Cantidad de SkillCoins")
    action_key = models.CharField(max_length=50, help_text="Clave interna, ej: 'complete_class'")

    def __str__(self):
        return f"[{self.get_mission_type_display()}] {self.title}"

class UserMission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="missions")
    template = models.ForeignKey(MissionTemplate, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    is_claimed = models.BooleanField(default=False)
    assigned_date = models.DateField(auto_now_add=True)

    def check_completion(self):
        if self.progress >= self.template.target_count and not self.is_completed:
            self.is_completed = True
            self.save()
            return True
        return False