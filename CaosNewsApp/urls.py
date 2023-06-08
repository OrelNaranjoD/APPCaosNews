from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.admin, name='admin'),
    path('actualidad', views.actualidad, name='actualidad'),
    path('', views.home, name='home'),
]