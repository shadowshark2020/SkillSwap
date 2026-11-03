from django.db import transaction

from .models import LedgerEntry, Wallet


class InsufficientFunds(Exception):
    pass


def _lock(*user_ids):
    wallets = (
        Wallet.objects.select_for_update()
        .filter(user_id__in=user_ids)
        .order_by("user_id")
    )
    return {w.user_id: w for w in wallets}


def _log(wallet, kind, amount, reference=""):
    return LedgerEntry.objects.create(
        wallet=wallet,
        kind=kind,
        amount=amount,
        balance_after=wallet.balance,
        held_after=wallet.held,
        reference=reference,
    )


@transaction.atomic
def credit(user, amount, kind, reference=""):
    """Bono, compra de tokens o recompensa de misión."""
    wallet = _lock(user.id)[user.id]
    wallet.balance += amount
    wallet.save(update_fields=["balance"])
    return _log(wallet, kind, amount, reference)


@transaction.atomic
def hold(user, amount, reference=""):
    """RF-08: reserva tokens al solicitar una tutoría."""
    wallet = _lock(user.id)[user.id]
    if wallet.available < amount:
        raise InsufficientFunds("Saldo insuficiente para reservar la tutoría.")
    wallet.held += amount
    wallet.save(update_fields=["held"])
    return _log(wallet, LedgerEntry.Kind.HOLD, amount, reference)


@transaction.atomic
def release(user, amount, reference=""):
    """Solicitud rechazada o cancelada: devuelve los tokens retenidos."""
    wallet = _lock(user.id)[user.id]
    if wallet.held < amount:
        raise ValueError("No hay suficientes tokens retenidos.")
    wallet.held -= amount
    wallet.save(update_fields=["held"])
    return _log(wallet, LedgerEntry.Kind.RELEASE, amount, reference)


@transaction.atomic
def settle(student, teacher, amount, reference=""):
    """RF-11: sesión finalizada, transfiere los tokens retenidos al Maestro."""
    wallets = _lock(student.id, teacher.id)
    s, t = wallets[student.id], wallets[teacher.id]
    if s.held < amount:
        raise ValueError("No hay suficientes tokens retenidos.")
    s.balance -= amount
    s.held -= amount
    t.balance += amount
    s.save(update_fields=["balance", "held"])
    t.save(update_fields=["balance"])
    _log(s, LedgerEntry.Kind.PAYMENT_OUT, amount, reference)
    _log(t, LedgerEntry.Kind.PAYMENT_IN, amount, reference)