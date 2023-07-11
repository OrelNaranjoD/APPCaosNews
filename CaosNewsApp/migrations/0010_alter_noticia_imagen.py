from django.db import migrations, models


def get_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    path = f"news/{instance.id_noticia}.{ext}"
    return path


class Migration(migrations.Migration):

    dependencies = [
        ('CaosNewsApp', '0009_alter_noticia_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to=get_image_upload_path),
        ),
    ]
