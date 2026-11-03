from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.IntegerField(default=0)
    held = models.IntegerField(default=0)

    def __str__(self):
        return f"Monedero de {self.user.email} (Balance: {self.balance}, Retenido: {self.held})"


class LedgerEntry(models.Model):
    KIND_CHOICES = (
        ("welcome", "Bono de bienvenida"),
        ("transfer", "Transferencia"),
        ("adjust", "Ajuste manual"),
        ("hold", "Retención en custodia"),
        ("release", "Liberación de custodia"),
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
    )
    amount = models.IntegerField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    balance_after = models.IntegerField(default=0)
    held_after = models.IntegerField(default=0)
    reference = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("El libro contable es inmutable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"[{self.kind}] {self.amount} SkillCoins - {self.wallet.user.email}"