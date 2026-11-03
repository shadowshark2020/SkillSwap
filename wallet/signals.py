from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Wallet
from .services import credit

User = get_user_model()
SKILLSWAP_WELCOME_BONUS = 20


@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Asegura la existencia del monedero
        Wallet.objects.get_or_create(user=instance)
        # Otorga el bono de bienvenida usando los parámetros exactos de tu servicio credit()
        credit(
            user=instance,
            amount=SKILLSWAP_WELCOME_BONUS,
            kind="welcome",
        )