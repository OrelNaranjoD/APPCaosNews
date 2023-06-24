from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from .models import Noticia, Profile
from django.contrib.auth import authenticate, login, logout
from .forms import NoticiaForm, LoginForm, RegisterForm
from django.http import JsonResponse
from django.contrib.auth.models import User
import requests




def index(request):
    noticias = Noticia.objects.raw('SELECT * FROM CaosNewsAPP_Noticia')
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'index.html', context)

def noticias(request, categoria):
    if categoria == 'Ultima Hora':
        noticias = Noticia.objects.order_by('-fecha_creacion')[:10]
    else:
        noticias = Noticia.objects.filter(id_categoria__nombre_categoria=categoria).order_by('-fecha_creacion')
    context={"noticias":noticias, "categoria": categoria}
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
            # Obtener los datos del formulario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            # Validar los campos individualmente
            errors = {}
            if User.objects.filter(username=username).exists():
                errors['username_error'] = True
            if len(password) < 6:
                errors['password_error'] = True

            if errors:
                # Hay errores, enviar la respuesta JSON con los errores
                return JsonResponse({'valid': False, **errors})
            else:
                # No hay errores, crear el usuario y guardarlo en la base de datos
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, )
                user.save()
                
                # Crear el perfil del usuario y guardarlo
                profile = Profile(user=user, role='lector')
                profile.save()

                # Enviar la respuesta JSON indicando que el registro fue exitoso
                return redirect('home')
        else:
            # El formulario no es válido, enviar la respuesta JSON con los errores del formulario
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
        noticias = Noticia.objects.all()
    else:
        noticias = Noticia.objects.filter(id_usuario=request.user.id)
    return render(request, 'admin/admin_noticias.html', {'noticias': noticias})

def admin_crear_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin/admin_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'admin/admin_crear_noticia.html', {'form': form})

def admin_editar_noticia(request, noticia_id):
    noticia = Noticia.objects.get(id_noticia=noticia_id)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('admin/admin_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'admin/admin_editar_noticia.html', {'form': form, 'noticia_id': noticia_id})


def admin_eliminar_noticia(request, noticia_id):
    noticia = Noticia.objects.get(id_noticia=noticia_id)
    noticia.delete()
    return redirect('admin/admin_noticias')

def admin_categoria(request):
    noticias = Noticia.objects.all()
    return render(request, 'admin/admin_categorias.html', {'noticias': noticias})

def admin_guardar_noticia(request, noticia_id=None):
    if noticia_id:
        noticia = Noticia.objects.get(id=noticia_id)
    else:
        noticia = None

    if request.method == 'POST':
        form = NoticiaForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('admin/admin_noticia')
    else:
        form = NoticiaForm(instance=noticia)

    context = {'form': form}
    return render(request, 'admin/admin_editar_noticia.html', context)

#Testing
def test(request):
    return render(request, 'test.html')