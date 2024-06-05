from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Noticia, ImagenNoticia, Categoria, Pais, DetalleNoticia

class NoticiaSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(write_only=True)
    imagen_nombre = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(source='id_noticia', read_only=True)
    titulo = serializers.CharField(source='titulo_noticia')
    cuerpo = serializers.CharField(source='cuerpo_noticia')

    class Meta:
        model = Noticia
        fields = ['id', 'fecha_creacion', 'titulo', 'cuerpo', 'imagen', 'imagen_nombre']

    def create(self, validated_data):
        imagen_data = validated_data.pop('imagen')
        imagen_nombre_original = imagen_data.name
        validated_data['id_categoria'] = Categoria.objects.get(id_categoria=14)
        validated_data['id_pais'] = Pais.objects.get(id_pais=1)
        validated_data['activo'] = True
        validated_data['destacada'] = False
        validated_data['id_usuario'] = User.objects.get(id=5)
        validated_data['eliminado'] = False
        noticia = super().create(validated_data)

        DetalleNoticia.objects.update_or_create(
            noticia=noticia,
            defaults={
                'comentario': 'Noticia creada por API',
                'estado': 'A',
                'publicada': True,
                'id_usuario': User.objects.get(id=5)
            }
        )

        ImagenNoticia.objects.create(noticia=noticia, imagen=imagen_data)
        noticia.imagen_nombre = imagen_nombre_original

        return noticia

    def get_imagen_nombre(self, obj):
        return getattr(obj, 'imagen_nombre', None)