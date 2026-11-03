from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        # Traemos las últimas 15 notificaciones del usuario
        notifs = Notification.objects.filter(recipient=request.user)[:15]
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'user_notifications': notifs,
            'unread_notifications_count': unread_count
        }
    return {}