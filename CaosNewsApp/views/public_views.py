from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Noticia, Comentario
from ..forms import ComentarioForm, RespuestaComentarioForm
from .utils import obtener_tiempo_chile


def index(request):
    """Vista principal con todas las noticias publicadas"""
    noticias = Noticia.objects.filter(detalle__publicada=True)
    context = {
        "noticias": noticias,
    }
    return render(request, "index.html", context)


def noticias(request, categoria):
    """Vista para mostrar noticias por categoría"""
    if categoria == "Ultima Hora":
        noticias = (
            Noticia.objects.filter(
                eliminado=False, activo=True, detalle__publicada=True
            )
            .exclude(id_categoria=14)
            .order_by("-fecha_creacion")
        )
    else:
        noticias = Noticia.objects.filter(
            id_categoria__nombre_categoria=categoria,
            eliminado=False,
            activo=True,
            detalle__publicada=True,
        ).order_by("-fecha_creacion")

    # Configurar paginación
    paginator = Paginator(noticias, 9)  # 9 noticias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "noticias": page_obj,
        "categoria": categoria,
        "page_obj": page_obj,
        "paginator": paginator,
    }
    return render(request, "noticia.html", context)


def mostrar_noticia(request, noticia_id):
    """Vista para mostrar el detalle de una noticia específica con comentarios"""
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id, activo=True)
    imagenes = noticia.imagenes.all()

    # Obtener comentarios principales (no respuestas) con paginación
    comentarios_principales = Comentario.objects.filter(
        noticia=noticia,
        activo=True,
        comentario_padre=None  # Solo comentarios principales
    ).select_related('usuario').prefetch_related('respuestas__usuario')

    # Configurar paginación para comentarios
    paginator = Paginator(comentarios_principales, 5)  # 5 comentarios por página
    page_number = request.GET.get('comentarios_page', 1)
    comentarios_page = paginator.get_page(page_number)

    # Preparar formularios
    comentario_form = ComentarioForm()
    respuesta_form = RespuestaComentarioForm()

    context = {
        "noticia": noticia,
        "imagenes": imagenes,
        "comentarios": comentarios_page,
        "comentario_form": comentario_form,
        "respuesta_form": respuesta_form,
        "total_comentarios": comentarios_principales.count(),
    }
    return render(request, "detalle_noticia.html", context)


def home(request):
    """Vista de la página principal con noticias destacadas y recientes"""
    noticias_destacadas = (
        Noticia.objects.filter(
            destacada=True, eliminado=False, activo=True, detalle__publicada=True
        )
        .exclude(id_categoria=14)
        .order_by("-fecha_creacion")
    )
    noticias_recientes = (
        Noticia.objects.filter(
            destacada=False, eliminado=False, activo=True, detalle__publicada=True
        )
        .exclude(id_categoria=14)
        .order_by("-fecha_creacion")[:5]
    )

    imagenes_destacadas = [noticia.imagenes.first() for noticia in noticias_destacadas]
    imagenes_recientes = [noticia.imagenes.first() for noticia in noticias_recientes]

    resultados_tiempo_chile = obtener_tiempo_chile()
    context = {
        "noticias_destacadas": noticias_destacadas,
        "noticias_recientes": noticias_recientes,
        "resultados_tiempo_chile": resultados_tiempo_chile,
        "imagenes_destacadas": imagenes_destacadas,
        "imagenes_recientes": imagenes_recientes,
    }
    return render(request, "home.html", context)


def busqueda(request):
    """Vista para búsqueda de noticias"""
    query = request.GET.get("q", "").strip()

    # Si no hay query o está vacío, mostrar todas las noticias
    if not query:
        noticias = Noticia.objects.filter(
            activo=True,
            eliminado=False,
            detalle__publicada=True
        ).order_by('-fecha_creacion')
    else:
        # Realizar búsqueda específica
        terms = query.split()
        q_objects = Q()

        for term in terms:
            q_objects |= Q(id_usuario__first_name__icontains=term) | Q(
                id_usuario__last_name__icontains=term
            )

        q_objects |= (
            Q(id_categoria__nombre_categoria__icontains=query)
            | Q(titulo_noticia__icontains=query)
            | Q(cuerpo_noticia__icontains=query)
        )

        # Filtrar solo noticias activas, publicadas y no eliminadas
        noticias = Noticia.objects.filter(
            q_objects,
            activo=True,
            eliminado=False,
            detalle__publicada=True
        ).order_by('-fecha_creacion')

    # Configurar paginación
    paginator = Paginator(noticias, 9)  # 9 noticias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "query": query,
        "noticias": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
    }
    return render(request, "busqueda.html", context)


def contacto(request):
    """Vista de la página de contacto"""
    return render(request, "contacto.html")


def footer(request):
    """Vista del footer"""
    return render(request, "footer.html")


def shop(request):
    """Vista de la tienda/shop"""
    return render(request, "shop.html")
