from django.contrib import admin
from .models import Noticia, Categoria

class NoticiaAdmin(admin.ModelAdmin):
    exclude = ('id_usuario',)

    def save_model(self, request, obj, form, change):
        if not obj.id_usuario_id:
            obj.id_usuario = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Categoria)