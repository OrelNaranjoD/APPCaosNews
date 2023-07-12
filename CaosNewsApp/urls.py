from django.urls import path , re_path
from django.conf import settings
from django.views.static import serve

from . import views

urlpatterns = [
    path('noticia/<int:noticia_id>/', views.mostrar_noticia, name='noticia_detalle'),
    path('noticias/<str:categoria>/', views.noticias, name='noticias'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto'),
    
    
    #Rutas de administrador
    path('admin/', views.admin_home, name='admin_home'),
    path('admin/noticias/', views.admin_noticias, name='admin_noticias'),
    path('admin/noticias/borradores', views.admin_noticias_borradores, name='admin_noticias_borradores'),
    path('admin/noticias/eliminadas', views.admin_noticias_eliminadas, name='admin_noticias_eliminadas'),
    path('admin/noticias/rechazadas', views.admin_noticias_rechazadas, name='admin_noticias_rechazadas'),
    path('admin/noticias/crear/', views.admin_crear_noticia, name='admin_crear_noticia'),
    path('admin/noticias/editar/<int:noticia_id>/', views.admin_editar_noticia, name='admin_editar_noticia'),
    path('admin/noticias/eliminar/<int:noticia_id>/', views.admin_eliminar_noticia, name='admin_eliminar_noticia'),
    path('admin/noticias/delete/<int:noticia_id>/', views.admin_delete_noticia, name='admin_delete_noticia'),
    path('admin/noticias/imagen/eliminar/<int:imagen_id>/', views.admin_eliminar_imagen_noticia, name='admin_eliminar_imagen'),
    path('admin/categorias/', views.admin_categoria, name='admin_categorias'),
    path('admin/perfil/editar/', views.admin_edit_profile, name='admin_editar_perfil'),
    path('admin/perfil/', views.admin_view_profile, name='admin_perfil'),
    
    #Ruta de testing
    path('test', views.test, name='test'),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
]