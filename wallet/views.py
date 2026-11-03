from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Wallet, LedgerEntry


@login_required
def wallet_detail(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    entries = LedgerEntry.objects.filter(wallet=wallet).order_by("-created_at")

    context = {
        "wallet": wallet,
        "entries": entries,
    }
    return render(request, "wallet/wallet.html", context)