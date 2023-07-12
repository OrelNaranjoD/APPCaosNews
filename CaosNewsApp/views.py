from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from .models import Noticia, Usuario, Categoria, ImagenNoticia, Pais
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import NoticiaForm, LoginForm, RegisterForm, UserProfileForm, DetalleNoticiaForm
from django.http import JsonResponse
from django.contrib.auth.models import User
import requests, sys, os
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q, Count, Value
from django.db.models.functions import Concat
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test

def index(request):
    noticias = Noticia.objects.filter(detalle__publicada=True)
    context = {
        'noticias': noticias,
    }
    return render(request, 'index.html', context)

def noticias(request, categoria):
    if categoria == 'Ultima Hora':
        noticias = Noticia.objects.filter(eliminado=False,  activo=True, detalle__publicada=True).order_by('-fecha_creacion')[:10]
    else:
        noticias = Noticia.objects.filter(id_categoria__nombre_categoria=categoria, eliminado=False,  activo=True, detalle__publicada=True).order_by('-fecha_creacion')
    context = {
        "noticias": noticias,
        "categoria": categoria,
    }
    return render(request, 'noticia.html', context)

def mostrar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    imagenes = noticia.imagenes.all()
    context = {
        'noticia': noticia,
        'imagenes': imagenes,
    }
    return render(request, 'detalle_noticia.html', context)

# Diccionario para almacenar en caché los datos del clima
cache_clima = {}
def obtener_tiempo_chile():
    url = 'http://api.openweathermap.org/data/2.5/weather?'
    api_key = 'cda050505a9bfed7a75a0663acda7e5a'
    ciudades_chile = ['Santiago', 'Antofagasta', 'Vina del Mar', 'Concepcion', 'Temuco']

    resultados = []

    for ciudad in ciudades_chile:
        if ciudad in cache_clima:
            ciudad_info = cache_clima[ciudad]
            resultados.append(ciudad_info)
        else:
            params = {
                'appid': api_key,
                'q': ciudad + ',cl',
                'units': 'metric',
                'lang': 'es',
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                ciudad_info = {
                    'ciudad': data['name'],
                    'temperatura': data['main']['temp'],
                    'temperatura_min': data['main']['temp_min'],
                    'temperatura_max': data['main']['temp_max'],
                    'tiempo': data['weather'][0]['description'],
                    'icono': data['weather'][0]['icon']
                }
                resultados.append(ciudad_info)
                cache_clima[ciudad] = ciudad_info
            else:
                print(f"Error en la solicitud para la ciudad {ciudad}: {response.status_code}")

    return resultados

def home(request):
    noticias_destacadas = Noticia.objects.filter(destacada=True, eliminado=False, activo=True, detalle__publicada=True).order_by('-fecha_creacion')
    noticias_recientes = Noticia.objects.filter(destacada=False, eliminado=False, activo=True, detalle__publicada=True).order_by('-fecha_creacion')[:3]

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
    return render(request, 'home.html', context)

def busqueda(request):
    query = request.GET.get('q')
    terms = query.split()

    q_objects = Q()

    for term in terms:
        q_objects |= Q(id_usuario__first_name__icontains=term) | Q(id_usuario__last_name__icontains=term)

    q_objects |= Q(id_categoria__nombre_categoria__icontains=query) | Q(titulo_noticia__icontains=query) | Q(cuerpo_noticia__icontains=query)

    noticias = Noticia.objects.filter(q_objects)
    context = {
        'query': query,
        'noticias': noticias
    }
    return render(request, 'busqueda.html', context)

def contacto(request):
    return render(request, 'contacto.html')

def footer(request):
    return render(request, 'footer.html')

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        if not identifier or not password:
            return JsonResponse({'valid': False, 'error_message': 'Por favor, complete todos los campos.'})
        user = User.objects.filter(Q(email=identifier) | Q(username=identifier)).first()
        if user is not None:
            if user.check_password(password):
                login(request, user)
                return JsonResponse({'valid': True, 'success_message': 'Inicio de sesión exitoso.'})
            else:
                return JsonResponse({'valid': False, 'error_message': 'Contraseña no válida.'})
        else:
            return JsonResponse({'valid': False, 'error_message': 'Correo electrónico o usuario no válido.'})

    return JsonResponse({'valid': False, 'error_message': 'Método de solicitud no válido.'})

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'valid': False, 'error_message': 'El nombre de usuario ya está en uso.'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'valid': False, 'error_message': 'El correo electrónico ya está registrado.'})

        if password != confirm_password:
            return JsonResponse({'valid': False, 'error_message': 'Las contraseñas no coinciden.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        login(request, user)

        return JsonResponse({'valid': True, 'success_message': 'Registro exitoso. Inicie sesión para continuar.'})

    return JsonResponse({'valid': False, 'error_message': 'Método de solicitud no válido.'})

def logout_view(request):
    logout(request)
    return redirect('home') 
    
    
#Vistas de Administrador
#Autorizacion de usuarios
def es_admin_periodista_o_editor(user):
    return user.groups.filter(name__in=['Administrador', 'Periodista', 'Editor']).exists()

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_home(request):
    if request.user.groups.filter(name='Administrador').exists():
        num_noticias_publicadas = Noticia.objects.filter(activo=True, detalle__publicada=True).count()
        num_noticias_pendientes = Noticia.objects.filter(detalle__publicada=False, detalle__estado__isnull=True).count()
    else:
        num_noticias_publicadas = Noticia.objects.filter(id_usuario=request.user, activo=True, detalle__publicada=True).count()
        num_noticias_pendientes = Noticia.objects.filter(id_usuario=request.user, detalle__publicada=False, detalle__estado__isnull=True).count()

    context = {
        'num_noticias_publicadas': num_noticias_publicadas,
        'num_noticias_pendientes': num_noticias_pendientes,
    }
    return render(request, 'admin/admin_home.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_noticias(request):
    if request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=False, activo=True, detalle__publicada=True, detalle__estado='A')
    else:
        noticias = Noticia.objects.filter(id_usuario=request.user.id, eliminado=False, activo=True, detalle__publicada=True, detalle__estado='A')
    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()
        
        context = {
        'noticias': noticias
    }
    return render(request, 'admin/admin_noticias.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_noticias_borradores(request):
    if request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=False, detalle__estado__isnull=True)
    else:
        noticias = Noticia.objects.filter(id_usuario=request.user.id, eliminado=False, detalle__publicada=False)
    
    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()
    
    context = {
        'noticias': noticias
    }
    
    return render(request, 'admin/admin_noticias_borradores.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_noticias_eliminadas(request):
    if request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=True)
    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()
        
    context = {
    'noticias': noticias
    }
    return render(request, 'admin/admin_noticias_eliminadas.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_noticias_rechazadas(request):
    if request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=False, detalle__estado='R')
    else:
        noticias = Noticia.objects.filter(id_usuario=request.user.id, eliminado=False, detalle__publicada=True, detalle__estado='R')
    
    for noticia in noticias:
        noticia.primer_imagen = noticia.imagenes.first()
    
    context = {
        'noticias': noticias
    }
    return render(request, 'admin/admin_noticias_rechazadas.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_crear_noticia(request):
    categorias = Categoria.objects.all()
    paises = Pais.objects.all()
    
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.id_usuario = request.user
            noticia.save()
            for imagen in request.FILES.getlist('imagenes'):
                    ImagenNoticia.objects.create(noticia=noticia, imagen=imagen)
            form.save_m2m()
            return redirect('admin_noticias_borradores')
    else:
        form = NoticiaForm()
    
    context = {
        'form': form,
        'categorias': categorias,
        'paises': paises
    }
    
    return render(request, 'admin/admin_crear_noticia.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_editar_noticia(request, noticia_id):
    noticia = Noticia.objects.get(id_noticia=noticia_id)
    categorias = Categoria.objects.all()
    paises = Pais.objects.all()
    imagenes = ImagenNoticia.objects.filter(noticia=noticia_id)

    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        detalle_form = DetalleNoticiaForm(request.POST, instance=noticia.detalle)
        if form.is_valid() and detalle_form.is_valid():
            noticia = form.save(commit=False)
            noticia.id_usuario = form.cleaned_data['id_usuario']
            noticia.save()
            form.save_m2m()

            if request.user.groups.filter(name='Administrador').exists():
                detalle = detalle_form.save(commit=False)
                detalle.noticia = noticia
                if detalle_form.cleaned_data['publicada']:
                    detalle.id_usuario = request.user
                    detalle.save()

            for imagen in request.FILES.getlist('imagenes'):
                ImagenNoticia.objects.create(noticia=noticia, imagen=imagen)

            return redirect('admin_noticias_borradores')
    else:
        form = NoticiaForm(instance=noticia)
        detalle_form = DetalleNoticiaForm(instance=noticia.detalle)

    context = {
        'form': form,
        'detalle_form': detalle_form,
        'categorias': categorias,
        'paises': paises,
        'noticia_id': noticia_id,
        'imagenes': imagenes
    }

    return render(request, 'admin/admin_editar_noticia.html', context)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_eliminar_imagen_noticia(request, imagen_id):
    imagen = get_object_or_404(ImagenNoticia, id_imagen=imagen_id)
    imagen.delete()
    return redirect('admin_editar_noticia', noticia_id=imagen.noticia.id_noticia)

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_eliminar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.eliminado = True
    noticia.save()
    return redirect('admin_noticias')

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_delete_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.delete()
    return redirect('admin_noticias_borradores')

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_categoria(request):
    noticias = Noticia.objects.all()
    return render(request, 'admin/admin_categorias.html', {'noticias': noticias})

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('admin_perfil')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'admin/admin_edit_profile.html', {'form': form})

@user_passes_test(es_admin_periodista_o_editor, login_url='home')
def admin_view_profile(request):
    return render(request, 'admin/admin_view_profile.html')

#Testing
def test(request):
    return render(request, 'test.html')