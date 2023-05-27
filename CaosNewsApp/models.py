from django.db import models

class Noticia(models.Model):
    id_noticia  = models.AutoField(db_column='id_noticia', primary_key=True) 
    titulo_noticia = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.titulo_noticia)