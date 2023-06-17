from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from .models import Noticia
from django.contrib.auth import authenticate, login, logout
from .forms import NoticiaForm, LoginForm
from django.http import JsonResponse

def index(request):
    noticias = Noticia.objects.raw('SELECT * FROM CaosNewsAPP_Noticia')
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'index.html', context)

def actualidad(request):
    noticias = Noticia.objects.all()
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'actualidad.html', context)

def home(request):
    return render(request, 'home.html')

def contacto(request):
    return render(request, 'contacto.html')

def footer(request):
    return render(request, 'footer.html')

def admin(request):
    return render(request, 'admin/admin.html')

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


def logout_view(request):
    logout(request)
    return redirect('home') 

def mostrar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    return render(request, 'detalle_noticia.html', {'noticia': noticia})
    
    
#Vistas de Administrador
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
            return redirect('vadmin_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'admin/admin_crear_noticia.html', {'form': form})

def admin_editar_noticia(request, noticia_id):
    noticia = Noticia.objects.get(id_noticia=noticia_id)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('admin_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'admin/admin_editar_noticia.html', {'form': form, 'noticia_id': noticia_id})

def admin_eliminar_noticia(request, noticia_id):
    noticia = Noticia.objects.get(id=noticia_id)
    noticia.delete()
    return redirect('admin/admin_noticias')

def admin_categoria(request):
    noticias = Noticia.objects.all()
    return render(request, 'admin/admin_categorias.html', {'noticias': noticias})

