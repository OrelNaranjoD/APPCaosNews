from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve

from . import views
# Importar vistas de comentarios
from .views import comentarios_views
# Importar vistas de administración
from .views import admin_views
# Importar vistas de autenticación
from .views import auth_views
# Importar vistas de pagos
from .views import payment_views
# Importar vistas de API
from .views import api_views
# Importar vistas utils
from .views import utils

# Removido app_name para evitar problemas con namespace en templates

urlpatterns = [
    path("noticia/<int:noticia_id>/", views.mostrar_noticia, name="noticia_detalle"),
    path("noticias/<str:categoria>/", views.noticias, name="noticias"),
    path("busqueda/", views.busqueda, name="busqueda"),

    # URLs del sistema de comentarios
    path("comentarios/obtener/<int:noticia_id>/", comentarios_views.obtener_comentarios, name="obtener_comentarios"),
    path("comentarios/crear/<int:noticia_id>/", comentarios_views.crear_comentario, name="crear_comentario"),
    path("comentarios/responder/<int:comentario_id>/", comentarios_views.crear_respuesta, name="crear_respuesta"),
    path("comentarios/eliminar/<int:comentario_id>/", comentarios_views.eliminar_comentario, name="eliminar_comentario"),

    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("register/", auth_views.register_view, name="register"),
    path("contacto/", views.contacto, name="contacto"),
    path("subscriptions/", views.subscriptions, name="subscriptions"),
    path("webpay/plus/commit/", payment_views.webpay_plus_commit, name="webpay-plus-commit"),
    path("webpay/plus/create/", payment_views.webpay_plus_create, name="webpay-plus-create"),
    path("", views.home, name="home"),
    # Rutas de administrador
    path("admin/", admin_views.admin_home, name="admin_home"),
    path("admin/noticias/", admin_views.admin_noticias, name="admin_noticias"),
    path(
        "admin/noticias/borradores/",
        admin_views.admin_noticias_borradores,
        name="admin_noticias_borradores",
    ),
    path(
        "admin/noticias/eliminadas/",
        admin_views.admin_noticias_eliminadas,
        name="admin_noticias_eliminadas",
    ),
    path(
        "admin/noticias/rechazadas/",
        admin_views.admin_noticias_rechazadas,
        name="admin_noticias_rechazadas",
    ),
    path(
        "admin/noticias/crear/", admin_views.admin_crear_noticia, name="admin_crear_noticia"
    ),
    path(
        "admin/noticias/editar/<int:noticia_id>/",
        admin_views.admin_editar_noticia,
        name="admin_editar_noticia",
    ),
    path(
        "admin/noticias/eliminar/<int:noticia_id>/",
        admin_views.admin_eliminar_noticia,
        name="admin_eliminar_noticia",
    ),
    path(
        "admin/noticias/restaurar/<int:noticia_id>/",
        admin_views.admin_restaurar_noticia,
        name="admin_restaurar_noticia",
    ),
    path(
        "admin/noticias/delete/<int:noticia_id>/",
        admin_views.admin_delete_noticia,
        name="admin_delete_noticia",
    ),
    path(
        "admin/noticias/imagen/eliminar/<int:imagen_id>/",
        admin_views.admin_eliminar_imagen_noticia,
        name="admin_eliminar_imagen",
    ),
    path("admin/categorias/", admin_views.admin_categoria, name="admin_categorias"),
    path("admin/perfil/editar/", admin_views.admin_edit_profile, name="admin_editar_perfil"),
    path("admin/perfil/", admin_views.admin_view_profile, name="admin_perfil"),
    path("admin/usuarios/", admin_views.admin_user_priv, name="admin_user_priv"),    # Rutas de administración de comentarios
    path("admin/comentarios/", admin_views.admin_comentarios, name="admin_comentarios"),
    path("admin/comentarios/toggle/<int:comentario_id>/", admin_views.admin_comentario_toggle_estado, name="admin_comentario_toggle_estado"),
    path("admin/comentarios/eliminar/<int:comentario_id>/", admin_views.admin_comentario_eliminar, name="admin_comentario_eliminar"),

    # Rutas de panel de usuario
    path("usuario/panel/", admin_views.user_panel, name="user_panel"),
    path("usuario/perfil/editar/", admin_views.user_edit_profile, name="user_edit_profile"),
    path("usuario/comentario/eliminar/<int:comentario_id>/", admin_views.user_delete_comment, name="user_delete_comment"),

    # Rutas API REST
    path("api/", api_views.api_root, name="api_root"),
    path("api/publicidad/", api_views.create_noticia, name="create_noticia"),
    # Ruta de testing
    path("test", utils.test, name="test"),
]

urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]
