from django.contrib import admin
from .models import Wallet, LedgerEntry


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
    search_fields = ("user__email",)


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount", "kind", "created_at")
    list_filter = ("kind",)
    search_fields = ("wallet__user__email",)

    # Bloquea añadir o editar manualmente, pero permite eliminar al borrar usuarios
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True