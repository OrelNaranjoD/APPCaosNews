from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Noticia
from django.contrib.auth import authenticate, login
from .forms import NoticiaForm

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
    
def mostrar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id_noticia=noticia_id)
    return render(request, 'detalle_noticia.html', {'noticia': noticia})
    
    
#Vistas de Administrador
def admin_noticias(request):
    noticias = Noticia.objects.all()
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

