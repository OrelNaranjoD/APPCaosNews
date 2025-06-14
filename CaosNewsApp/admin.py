from django.contrib import admin
from .models import Noticia, Categoria, ImagenNoticia, Pais, DetalleNoticia, Comentario

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id_comentario', 'noticia', 'usuario', 'contenido_truncado', 'fecha_creacion', 'activo', 'es_respuesta')
    list_filter = ('activo', 'fecha_creacion', 'comentario_padre')
    search_fields = ('contenido', 'usuario__first_name', 'usuario__last_name', 'noticia__titulo_noticia')
    list_editable = ('activo',)
    ordering = ('-fecha_creacion',)

    def contenido_truncado(self, obj):
        return obj.contenido[:50] + "..." if len(obj.contenido) > 50 else obj.contenido
    contenido_truncado.short_description = 'Contenido'

    def es_respuesta(self, obj):
        return obj.comentario_padre is not None
    es_respuesta.boolean = True
    es_respuesta.short_description = 'Es respuesta'

admin.site.register(Noticia)
admin.site.register(ImagenNoticia)
admin.site.register(Categoria)
admin.site.register(Pais)
admin.site.register(DetalleNoticia)
