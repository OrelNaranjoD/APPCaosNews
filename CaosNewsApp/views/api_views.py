from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler
from ..serializers import NoticiaSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_noticia(request):
    """API para crear noticias a través de REST"""
    serializer = NoticiaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


def custom_exception_handler(exc, context):
    """Manejador personalizado de excepciones para la API"""
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail")
        if detail == "Las credenciales de autenticación no se proveyeron.":
            response.data["error"] = (
                "Las credenciales de autenticación no fueron incluidas."
            )
        elif detail == "Token inválido.":
            response.data["error"] = "El Token proporcionado es incorrecto."
        else:
            response.data["error"] = detail
        del response.data["detail"]

    return response
