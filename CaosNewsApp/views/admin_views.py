from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from ..models import Noticia, Categoria, Pais, ImagenNoticia
from ..forms import NoticiaForm, UserProfileForm, DetalleNoticiaForm


# Funciones de autorización
def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.groups.filter(name__in=["Administrador"]).exists()


def es_admin_periodista_o_editor(user):
    """Verifica si el usuario es administrador, periodista o editor"""
    return user.groups.filter(
        name__in=["Administrador", "Periodista", "Editor"]
    ).exists()


# Vistas de administración
@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_home(request):
    """Panel principal del administrador"""
    if request.user.groups.filter(name="Administrador").exists():
        # Estadísticas para administrador (todas las noticias)
        num_noticias_publicadas = Noticia.objects.filter(
            activo=True,
            eliminado=False,
            detalle__publicada=True,
            detalle__estado="A"
        ).count()

        num_noticias_pendientes = Noticia.objects.filter(
            eliminado=False,
            detalle__publicada=False,
            detalle__estado__isnull=True
        ).count()

        num_noticias_rechazadas = Noticia.objects.filter(
            eliminado=False,
            detalle__estado="R"
        ).count()

        num_noticias_eliminadas = Noticia.objects.filter(
            eliminado=True
        ).count()

        num_noticias_inactivas = Noticia.objects.filter(
            activo=False,
            eliminado=False
        ).count()

        # Total de noticias (no eliminadas)
        total_noticias = Noticia.objects.filter(eliminado=False).count()

        # Estadísticas adicionales
        num_autores_activos = Noticia.objects.filter(
            eliminado=False,
            detalle__publicada=True
        ).values('id_usuario').distinct().count()

    else:
        # Estadísticas para periodistas/editores (solo sus noticias)
        num_noticias_publicadas = Noticia.objects.filter(
            id_usuario=request.user,
            activo=True,
            eliminado=False,
            detalle__publicada=True,
            detalle__estado="A"
        ).count()

        num_noticias_pendientes = Noticia.objects.filter(
            id_usuario=request.user,
            eliminado=False,
            detalle__publicada=False,
            detalle__estado__isnull=True,
        ).count()

        num_noticias_rechazadas = Noticia.objects.filter(
            id_usuario=request.user,
            eliminado=False,
            detalle__estado="R"
        ).count()

        num_noticias_eliminadas = Noticia.objects.filter(
            id_usuario=request.user,
            eliminado=True
        ).count()

        num_noticias_inactivas = Noticia.objects.filter(
            id_usuario=request.user,
            activo=False,
            eliminado=False
        ).count()

        # Total de noticias del usuario (no eliminadas)
        total_noticias = Noticia.objects.filter(
            id_usuario=request.user,
            eliminado=False
        ).count()

        num_autores_activos = None  # No relevante para no administradores

    context = {
        "num_noticias_publicadas": num_noticias_publicadas,
        "num_noticias_pendientes": num_noticias_pendientes,
        "num_noticias_rechazadas": num_noticias_rechazadas,
        "num_noticias_eliminadas": num_noticias_eliminadas,
        "num_noticias_inactivas": num_noticias_inactivas,
        "total_noticias": total_noticias,
        "num_autores_activos": num_autores_activos,
        "es_administrador": request.user.groups.filter(name="Administrador").exists(),
    }
    return render(request, "admin/admin_home.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_noticias(request):
    """Vista para noticias publicadas"""
    if request.user.groups.filter(name="Administrador").exists():
        noticias = Noticia.objects.filter(
            eliminado=False, activo=True, detalle__publicada=True, detalle__estado="A"
        )
    else:
        noticias = Noticia.objects.filter(
            id_usuario=request.user.id,
            eliminado=False,
            activo=True,
            detalle__publicada=True,
            detalle__estado="A",
        )
    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()

    context = {"noticias": noticias}
    return render(request, "admin/admin_noticias.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_noticias_borradores(request):
    """Vista para noticias en borrador"""
    if request.user.groups.filter(name="Administrador").exists():
        noticias = Noticia.objects.filter(eliminado=False, detalle__estado__isnull=True)
    else:
        noticias = Noticia.objects.filter(
            id_usuario=request.user.id, eliminado=False, detalle__publicada=False
        )

    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()

    context = {"noticias": noticias}

    return render(request, "admin/admin_noticias_borradores.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_noticias_eliminadas(request):
    """Vista para noticias eliminadas"""
    if request.user.groups.filter(name="Administrador").exists():
        noticias = Noticia.objects.filter(eliminado=True)
    else:
        noticias = Noticia.objects.filter(
            id_usuario=request.user.id,
            eliminado=True
        )

    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()

    context = {"noticias": noticias}
    return render(request, "admin/admin_noticias_eliminadas.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_noticias_rechazadas(request):
    """Vista para noticias rechazadas"""
    if request.user.groups.filter(name="Administrador").exists():
        noticias = Noticia.objects.filter(eliminado=False, detalle__estado="R")
    else:
        noticias = Noticia.objects.filter(
            id_usuario=request.user.id,
            eliminado=False,
            detalle__publicada=True,
            detalle__estado="R",
        )

    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()

    context = {"noticias": noticias}
    return render(request, "admin/admin_noticias_rechazadas.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_crear_noticia(request):
    """Vista para crear nueva noticia"""
    categorias = Categoria.objects.all()
    paises = Pais.objects.all()

    if request.method == "POST":
        print(f"📝 POST data received: {request.POST}")
        form = NoticiaForm(request.POST, request.FILES)
        print(f"📋 Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"❌ Form errors: {form.errors}")

        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.id_usuario = request.user
            print(f"👤 Usuario asignado: {noticia.id_usuario}")
            print(f"📁 Categoría: {noticia.id_categoria}")
            print(f"🌍 País: {noticia.id_pais}")
            print(f"📰 Título: {noticia.titulo_noticia}")

            try:
                noticia.save()
                print("✅ Noticia guardada exitosamente")
                for imagen in request.FILES.getlist("imagenes"):
                    ImagenNoticia.objects.create(noticia=noticia, imagen=imagen)
                form.save_m2m()
                return redirect("admin_noticias_borradores")
            except Exception as e:
                print(f"❌ Error al guardar noticia: {e}")
                import traceback
                traceback.print_exc()
    else:
        form = NoticiaForm()

    context = {"form": form, "categorias": categorias, "paises": paises}

    return render(request, "admin/admin_crear_noticia.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_editar_noticia(request, noticia_id):
    """Vista para editar noticia existente"""
    noticia = Noticia.objects.get(id_noticia=noticia_id)
    categorias = Categoria.objects.all()
    paises = Pais.objects.all()
    imagenes = ImagenNoticia.objects.filter(noticia=noticia_id)

    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        detalle_form = DetalleNoticiaForm(request.POST, instance=noticia.detalle)
        if form.is_valid() and detalle_form.is_valid():
            noticia = form.save(commit=False)
            noticia.id_usuario = form.cleaned_data["id_usuario"]
            noticia.save()
            form.save_m2m()

            if request.user.groups.filter(name="Administrador").exists():
                detalle = detalle_form.save(commit=False)
                detalle.noticia = noticia
                if detalle_form.cleaned_data["publicada"]:
                    detalle.id_usuario = request.user
                    detalle.save()

            for imagen in request.FILES.getlist("imagenes"):
                ImagenNoticia.objects.create(noticia=noticia, imagen=imagen)

            return redirect("admin_noticias_borradores")
    else:
        form = NoticiaForm(instance=noticia)
        detalle_form = DetalleNoticiaForm(instance=noticia.detalle)

    context = {
        "form": form,
        "detalle_form": detalle_form,
        "categorias": categorias,
        "paises": paises,
        "noticia_id": noticia_id,
        "imagenes": imagenes,
    }

    return render(request, "admin/admin_editar_noticia.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_eliminar_imagen_noticia(request, imagen_id):
    """Vista para eliminar imagen de noticia"""
    imagen = get_object_or_404(ImagenNoticia, id_imagen=imagen_id)
    imagen.delete()
    return redirect("admin_editar_noticia", noticia_id=imagen.noticia.id_noticia)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_eliminar_noticia(request, noticia_id):
    """Vista para marcar noticia como eliminada"""
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.eliminado = True
    noticia.save()
    return redirect("admin_noticias")


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_delete_noticia(request, noticia_id):
    """Vista para eliminar permanentemente una noticia"""
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.delete()
    return redirect("admin_noticias_borradores")


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_categoria(request):
    """Vista para gestión de categorías"""
    noticias = Noticia.objects.all()
    return render(request, "admin/admin_categorias.html", {"noticias": noticias})


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_edit_profile(request):
    """Vista para editar perfil de usuario"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("admin_perfil")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "admin/admin_edit_profile.html", {"form": form})


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_view_profile(request):
    """Vista para mostrar perfil de usuario"""
    return render(request, "admin/admin_view_profile.html")


@user_passes_test(es_admin, login_url="home")
def admin_user_priv(request):
    """Vista para gestión de privilegios de usuarios"""
    user_model = get_user_model()
    lista_usuarios = user_model.objects.all()

    for usuario in lista_usuarios:
        if request.method == "POST":
            form = UserProfileForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
        else:
            form = UserProfileForm(instance=usuario)

        usuario.form = form

    context = {
        "lista_usuarios": lista_usuarios,
    }
    return render(request, "admin/admin_user_priv.html", context)


@user_passes_test(es_admin_periodista_o_editor, login_url="home")
def admin_restaurar_noticia(request, noticia_id):
    """Vista para restaurar noticia eliminada"""
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)

    # Verificar que el usuario tiene permisos para restaurar esta noticia
    if not request.user.groups.filter(name="Administrador").exists():
        # Si no es administrador, verificar que es el autor de la noticia
        if noticia.id_usuario != request.user:
            return redirect("admin_noticias_eliminadas")

    noticia.eliminado = False
    noticia.save()
    return redirect("admin_noticias_eliminadas")
