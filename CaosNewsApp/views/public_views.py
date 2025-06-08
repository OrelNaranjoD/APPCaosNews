from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from ..models import Noticia
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
            .order_by("-fecha_creacion")[:10]
        )
    else:
        noticias = Noticia.objects.filter(
            id_categoria__nombre_categoria=categoria,
            eliminado=False,
            activo=True,
            detalle__publicada=True,
        ).order_by("-fecha_creacion")
    context = {
        "noticias": noticias,
        "categoria": categoria,
    }
    return render(request, "noticia.html", context)


def mostrar_noticia(request, noticia_id):
    """Vista para mostrar el detalle de una noticia específica"""
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    imagenes = noticia.imagenes.all()
    context = {
        "noticia": noticia,
        "imagenes": imagenes,
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
    query = request.GET.get("q")
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

    noticias = Noticia.objects.filter(q_objects)
    context = {"query": query, "noticias": noticias}
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
