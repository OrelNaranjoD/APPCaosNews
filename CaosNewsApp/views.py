from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Noticia

def index(request):
    noticias = Noticia.objects.raw('SELECT * FROM CaosNewsAPP_Noticia')
    print(noticias)
    context={"noticias":noticias}
    return render(request, 'index.html', context)

def home(request):
    return render(request, 'home.html')

def footer(request):
    return render(request, 'footer.html')