# Generated by Django 4.2.1 on 2023-06-27 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CaosNewsApp', '0005_noticia_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='delete',
            field=models.BooleanField(default=False, verbose_name='Borrado'),
        ),
        migrations.AlterField(
            model_name='noticia',
            name='id_categoria',
            field=models.ForeignKey(db_column='id_categoria', on_delete=django.db.models.deletion.PROTECT, to='CaosNewsApp.categoria'),
        ),
    ]
