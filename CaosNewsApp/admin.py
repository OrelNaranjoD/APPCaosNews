from django.contrib import admin
from .models import Noticia
from .models import CustomUser

admin.site.register(Noticia)
admin.site.register(CustomUser)