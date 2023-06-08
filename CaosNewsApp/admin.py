from django.contrib import admin
from .models import Noticia, Categoria
from .models import CustomUser

admin.site.register(Noticia)
admin.site.register(CustomUser)
admin.site.register(Categoria)