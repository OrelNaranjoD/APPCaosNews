from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.admin, name='admin'),
    path('actualidad', views.actualidad, name='actualidad'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
]