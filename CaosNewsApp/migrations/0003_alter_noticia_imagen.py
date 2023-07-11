from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CaosNewsApp', '0002_alter_noticia_imagen_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='news/'),
        ),
    ]
