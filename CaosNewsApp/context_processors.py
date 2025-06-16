def search_query(request):
    """Context processor para que 'q' esté siempre disponible en los templates."""
    return {'q': request.GET.get('q', '')}
