from django.conf import settings

def analytics(request):
    """
    Injeta o ID do Google Analytics em todos os templates apenas se DEBUG=False.
    """
    if not settings.DEBUG:
        return {
            'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', None)
        }
    return {'GA_MEASUREMENT_ID': None}