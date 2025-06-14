from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import transaction
from django.urls import reverse
import json

from ..models import Noticia, Comentario
from ..forms import ComentarioForm, RespuestaComentarioForm


class ComentarioService:
    """Servicio para manejar la lógica de negocio de comentarios"""

    @staticmethod
    def obtener_comentarios_noticia(noticia_id, page=1, per_page=10):
        """Obtiene los comentarios principales de una noticia con paginación"""
        noticia = get_object_or_404(Noticia, id_noticia=noticia_id, activo=True)
        comentarios_principales = Comentario.objects.filter(
            noticia=noticia,
            activo=True,
            comentario_padre=None  # Solo comentarios principales, no respuestas
        ).select_related('usuario').prefetch_related('respuestas__usuario')

        paginator = Paginator(comentarios_principales, per_page)
        page_obj = paginator.get_page(page)

        return noticia, page_obj

    @staticmethod
    def crear_comentario(noticia_id, usuario, contenido):
        """Crea un nuevo comentario principal"""
        noticia = get_object_or_404(Noticia, id_noticia=noticia_id, activo=True)

        with transaction.atomic():
            comentario = Comentario.objects.create(
                noticia=noticia,
                usuario=usuario,
                contenido=contenido
            )

        return comentario

    @staticmethod
    def crear_respuesta(comentario_padre_id, usuario, contenido):
        """Crea una respuesta a un comentario existente"""
        comentario_padre = get_object_or_404(
            Comentario,
            id_comentario=comentario_padre_id,
            activo=True,
            comentario_padre=None  # Solo se puede responder a comentarios principales
        )

        with transaction.atomic():
            respuesta = Comentario.objects.create(
                noticia=comentario_padre.noticia,
                usuario=usuario,
                contenido=contenido,
                comentario_padre=comentario_padre
            )

        return respuesta

    @staticmethod
    def eliminar_comentario(comentario_id, usuario):
        """Elimina un comentario (solo el autor puede eliminarlo)"""
        comentario = get_object_or_404(Comentario, id_comentario=comentario_id, usuario=usuario)
        comentario.activo = False
        comentario.save()

        return comentario


@require_http_methods(["GET"])
def obtener_comentarios(request, noticia_id):
    """Vista para obtener comentarios de una noticia (AJAX)"""
    try:
        page = request.GET.get('page', 1)
        noticia, page_obj = ComentarioService.obtener_comentarios_noticia(noticia_id, page)

        # Renderizar solo la sección de comentarios
        html = render(request, 'components/comentarios_lista.html', {
            'noticia': noticia,
            'comentarios': page_obj,
            'page_obj': page_obj
        }).content.decode('utf-8')

        return JsonResponse({
            'success': True,
            'html': html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def crear_comentario(request, noticia_id):
    """Vista para crear un nuevo comentario"""
    form = ComentarioForm(request.POST)

    if form.is_valid():
        try:
            comentario = ComentarioService.crear_comentario(
                noticia_id=noticia_id,
                usuario=request.user,
                contenido=form.cleaned_data['contenido']
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Respuesta AJAX
                return JsonResponse({
                    'success': True,
                    'message': 'Comentario creado exitosamente',
                    'comentario_id': comentario.id_comentario
                })
            else:
                messages.success(request, 'Comentario agregado exitosamente')
                return redirect('noticia_detalle', noticia_id=noticia_id)

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            else:
                messages.error(request, f'Error al crear comentario: {str(e)}')
                return redirect('noticia_detalle', noticia_id=noticia_id)

    # Si el formulario no es válido
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    else:
        # Redirigir con errores para formulario no AJAX
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
        return redirect('noticia_detalle', noticia_id=noticia_id)


@login_required
@require_http_methods(["POST"])
def crear_respuesta(request, comentario_id):
    """Vista para crear una respuesta a un comentario"""
    form = RespuestaComentarioForm(request.POST)

    if form.is_valid():
        try:
            respuesta = ComentarioService.crear_respuesta(
                comentario_padre_id=comentario_id,
                usuario=request.user,
                contenido=form.cleaned_data['contenido']
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Respuesta AJAX
                return JsonResponse({
                    'success': True,
                    'message': 'Respuesta creada exitosamente',
                    'respuesta_id': respuesta.id_comentario
                })
            else:
                messages.success(request, 'Respuesta agregada exitosamente')
                return redirect('noticia_detalle', noticia_id=respuesta.noticia.id_noticia)

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            else:
                messages.error(request, f'Error al crear respuesta: {str(e)}')
                return redirect('noticia_detalle', noticia_id=comentario_id)

    # Si el formulario no es válido
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
        # Obtener la noticia desde el comentario padre para redirigir
        comentario_padre = get_object_or_404(Comentario, id_comentario=comentario_id)
        return redirect('noticia_detalle', noticia_id=comentario_padre.noticia.id_noticia)


@login_required
@require_http_methods(["POST"])
def eliminar_comentario(request, comentario_id):
    """Vista para eliminar un comentario (soft delete)"""
    try:
        comentario = ComentarioService.eliminar_comentario(comentario_id, request.user)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Comentario eliminado exitosamente'
            })
        else:
            messages.success(request, 'Comentario eliminado exitosamente')
            return redirect('noticia_detalle', noticia_id=comentario.noticia.id_noticia)

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        else:
            messages.error(request, f'Error al eliminar comentario: {str(e)}')
            return redirect('noticia_detalle', noticia_id=comentario_id)
