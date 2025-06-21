def search_query(request):
    """Context processor para que 'q' esté siempre disponible en los templates."""
    return {'q': request.GET.get('q', '')}


def notificaciones_usuario(request):
    """Context processor simple para notificaciones del usuario."""
    if request.user.is_authenticated:
        notificaciones = request.user.get_notificaciones_no_leidas()
        return {
            'notificaciones_pendientes': notificaciones,
            'tiene_notificaciones': request.user.tiene_notificaciones_pendientes()
        }
    return {
        'notificaciones_pendientes': [],
        'tiene_notificaciones': False
    }
