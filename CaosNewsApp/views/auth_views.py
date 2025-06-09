from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Q


def login_view(request):
    """Vista para el inicio de sesión"""
    user_model = get_user_model()  # Obtiene el modelo de usuario correcto según la configuración

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")
        if not identifier or not password:
            return JsonResponse(
                {
                    "valid": False,
                    "error_message": "Por favor, complete todos los campos.",
                }
            )
        user = user_model.objects.filter(Q(email=identifier) | Q(username=identifier)).first()
        if user is not None:
            if user.check_password(password):
                # Especificar el backend para evitar errores cuando hay múltiples backends
                user.backend = 'CaosNewsApp.backends.EmailOrUsernameModelBackend'
                login(request, user)
                return JsonResponse(
                    {"valid": True, "success_message": "Inicio de sesión exitoso."}
                )
            else:
                return JsonResponse(
                    {"valid": False, "error_message": "Contraseña no válida."}
                )
        else:
            return JsonResponse(
                {
                    "valid": False,
                    "error_message": "Correo electrónico o usuario no válido.",
                }
            )

    return JsonResponse(
        {"valid": False, "error_message": "Método de solicitud no válido."}
    )


def register_view(request):
    """Vista para el registro de nuevos usuarios"""
    user_model = get_user_model()  # Obtiene el modelo de usuario correcto según la configuración

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if user_model.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "valid": False,
                    "error_message": "El nombre de usuario ya está en uso.",
                }
            )

        if user_model.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "valid": False,
                    "error_message": "El correo electrónico ya está registrado.",
                }
            )

        if password != confirm_password:
            return JsonResponse(
                {"valid": False, "error_message": "Las contraseñas no coinciden."}
            )

        user = user_model.objects.create_user(
            username=username, email=email, password=password
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Especificar el backend para evitar errores cuando hay múltiples backends
        user.backend = 'CaosNewsApp.backends.EmailOrUsernameModelBackend'
        login(request, user)

        return JsonResponse(
            {
                "valid": True,
                "success_message": "Registro exitoso.",
            }
        )

    return JsonResponse(
        {"valid": False, "error_message": "Método de solicitud no válido."}
    )


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect("home")
