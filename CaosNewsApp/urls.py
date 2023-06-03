from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.admin, name='admin'),
    path('', views.home, name='home'),
]