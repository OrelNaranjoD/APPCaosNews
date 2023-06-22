from django.urls import path , re_path
from django.conf import settings
from django.views.static import serve

from . import views

urlpatterns = [
    path('noticia/<int:noticia_id>/', views.mostrar_noticia, name='noticia_detalle'),
    path('noticias/<str:categoria>/', views.noticias, name='noticias'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('contacto/', views.contacto, name='contacto'),
    
    
    #Rutas de administrador
    path('admin/', views.admin_home, name='admin_home'),
    path('admin/noticias/', views.admin_noticias, name='admin_noticias'),
    path('admin/noticias/crear/', views.admin_crear_noticia, name='admin_crear_noticia'),
    path('admin/noticias/editar/<int:noticia_id>/', views.admin_editar_noticia, name='admin_editar_noticia'),
    path('admin/noticias/eliminar/<int:noticia_id>/', views.admin_eliminar_noticia, name='admin_eliminar_noticia'),
    
    #Ruta de testing
    path('test', views.test, name='test'),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
]