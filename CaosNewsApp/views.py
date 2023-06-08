from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Noticia
from django.contrib.auth import authenticate, login

def index(request):
    noticias = Noticia.objects.raw('SELECT * FROM CaosNewsAPP_Noticia')
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'index.html', context)

def actualidad(request):
    noticias = Noticia.objects.raw('SELECT * FROM CaosNewsAPP_Noticia')
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'actualidad.html', context)

def home(request):
    return render(request, 'home.html')

def footer(request):
    return render(request, 'footer.html')

def admin(request):
    return render(request, 'admin/admin.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir al administrador personalizado
            return redirect('/admin')
        else:
            # El inicio de sesión falló, mostrar mensaje de error o realizar acciones adicionales
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    else:
        return render(request, 'login.html')