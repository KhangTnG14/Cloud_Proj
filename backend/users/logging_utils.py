from .models import SystemLog


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_system_action(request, action, details=None, user=None):
    actor = user
    if actor is None and hasattr(request, 'user') and request.user.is_authenticated:
        actor = request.user
    SystemLog.objects.create(
        user=actor,
        action=action,
        details=details,
        ip_address=get_client_ip(request),
    )
