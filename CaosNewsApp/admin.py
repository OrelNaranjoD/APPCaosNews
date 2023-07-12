from django.contrib import admin
from .models import Noticia, Categoria, ImagenNoticia, Pais, DetalleNoticia
 
admin.site.register(Noticia)
admin.site.register(ImagenNoticia)
admin.site.register(Categoria)
admin.site.register(Pais)
admin.site.register(DetalleNoticia)