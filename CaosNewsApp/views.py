from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from .models import Noticia, Usuario, Categoria
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import NoticiaForm, LoginForm, RegisterForm, UserProfileForm
from django.http import JsonResponse
from django.contrib.auth.models import User
import requests, sys
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
import os
from django.contrib.auth.models import Group



def index(request):
    noticias = Noticia.objects.all()
    if request.user.is_authenticated:
        is_lector = request.user.groups.filter(name='Lector').exists()
    else:
        is_lector = False
    context = {
        'noticias': noticias,
        'is_lector': is_lector,
    }
    return render(request, 'index.html', context)

def noticias(request, categoria):
    if categoria == 'Ultima Hora':
        noticias = Noticia.objects.filter(delete=False, activo=True).order_by('-fecha_creacion')[:10]
    else:
        noticias = Noticia.objects.filter(id_categoria__nombre_categoria=categoria, delete=False, activo=True).order_by('-fecha_creacion')
    context = {"noticias": noticias, "categoria": categoria}
    return render(request, 'noticia.html', context)

def mostrar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    return render(request, 'detalle_noticia.html', {'noticia': noticia})

def obtener_tiempo_chile():
    url = 'http://api.openweathermap.org/data/2.5/weather?'
    api_key = 'cda050505a9bfed7a75a0663acda7e5a'
    ciudades_chile = ['Santiago', 'Antofagasta', 'Vina del Mar', 'Concepcion', 'Temuco'] 

    resultados = []

    for ciudad in ciudades_chile:
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
        else:
            print(f"Error en la solicitud para la ciudad {ciudad}: {response.status_code}")

    return resultados

def home(request):
    resultados_tiempo_chile = obtener_tiempo_chile()
    context = {'resultados_tiempo_chile': resultados_tiempo_chile}  
    return render(request, 'home.html', context)

def contacto(request):
    return render(request, 'contacto.html')

def footer(request):
    return render(request, 'footer.html')



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False, 'username_error': True, 'password_error': False})
        else:
            return JsonResponse({'valid': False, 'username_error': False, 'password_error': False})
    
    return JsonResponse({'valid': False, 'username_error': False, 'password_error': False})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            
            errors = {}
            if User.objects.filter(username=username).exists():
                errors['username_error'] = True
            if len(password) < 6:
                errors['password_error'] = True

            if errors:
                return JsonResponse({'valid': False, **errors})
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, )
                user.save()
        
                profile = Profile(user=user, role='lector')
                profile.save()
                return redirect('home')
        else:
            form_errors = form.errors.as_json()
            return JsonResponse({'valid': False, 'form_errors': form_errors})
    else:
        form = RegisterForm()
    
    return render(request, 'index.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home') 
    
    
#Vistas de Administrador
def admin_home(request):
    return render(request, 'admin/admin_home.html')

def admin_noticias(request):
    if request.user.groups.exists() and request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=False, activo=True)
        is_admin = True
    else:
        is_admin = False
        noticias = Noticia.objects.filter(id_usuario=request.user.id, eliminado=False, activo=True)
    return render(request, 'admin/admin_noticias.html', {'noticias': noticias, 'is_admin': is_admin})

def admin_noticias_borradores(request):
    if request.user.groups.exists() and request.user.groups.filter(name='Administrador').exists():
        noticias = Noticia.objects.filter(eliminado=True) | Noticia.objects.filter(activo=False)
        is_admin = True 
    else:
        is_admin = False
        noticias = Noticia.objects.filter(id_usuario=request.user.id, eliminado=True) | Noticia.objects.filter(id_usuario=request.user.id, activo=False)
    return render(request, 'admin/admin_noticias_borradores.html', {'noticias': noticias, 'is_admin': is_admin})

def admin_crear_noticia(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.id_usuario = request.user  
            noticia.save()
            
            imagen = request.FILES.get('imagen')
            if imagen:
                extension = os.path.splitext(imagen.name)[-1]
                nombre_archivo = f'{noticia.id_noticia}{extension}'
                noticia.imagen.name = f'news/{nombre_archivo}'
                noticia.save()

            return redirect('admin_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'admin/admin_crear_noticia.html', {'form': form, 'categorias': categorias})

def admin_editar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            print("Actualización exitosa")
            return redirect('admin_noticias')
        else:
            print("Formulario no válido:", form.errors)
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'admin/admin_editar_noticia.html', {'form': form, 'noticia_id': noticia_id, 'categorias': categorias})

def admin_eliminar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.eliminado = True
    noticia.save()
    return redirect('admin_noticias')

def admin_delete_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    noticia.delete()
    return redirect('admin_noticias_borradores')

def admin_categoria(request):
    noticias = Noticia.objects.all()
    return render(request, 'admin/admin_categorias.html', {'noticias': noticias})

@login_required
def admin_edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('admin_perfil')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'admin/admin_edit_profile.html', {'form': form})

@login_required
def admin_view_profile(request):
    return render(request, 'admin/admin_view_profile.html')

#Testing
def test(request):
    return render(request, 'test.html')