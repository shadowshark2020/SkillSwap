def wallet_balance(request):
    """Expone el monedero del usuario en todas las plantillas."""
    user = request.user
    if user.is_authenticated:
        return {"wallet": getattr(user, "wallet", None)}
    return {}