# Generated manually to fix foreign key constraint issue
# Fixes the foreign key reference from auth_user to CaosNewsApp_usuario

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CaosNewsApp', '0022_alter_detallenoticia_estado_and_more'),
    ]

    operations = [
        # First, remove the old foreign key constraint
        migrations.RunSQL(
            "PRAGMA foreign_keys=OFF;",
            reverse_sql="PRAGMA foreign_keys=ON;"
        ),

        # Create a new table with the correct foreign key
        migrations.RunSQL(
            """
            CREATE TABLE "CaosNewsApp_noticia_new" (
                "id_noticia" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "titulo_noticia" varchar(100) NOT NULL,
                "cuerpo_noticia" text NOT NULL,
                "activo" bool NOT NULL,
                "fecha_creacion" datetime NOT NULL,
                "fecha_modificacion" datetime NOT NULL,
                "id_categoria" integer NOT NULL REFERENCES "CaosNewsApp_categoria" ("id_categoria") DEFERRABLE INITIALLY DEFERRED,
                "id_usuario" integer NOT NULL REFERENCES "CaosNewsApp_usuario" ("id") DEFERRABLE INITIALLY DEFERRED,
                "eliminado" bool NOT NULL,
                "destacada" bool NOT NULL,
                "id_pais" integer NULL REFERENCES "CaosNewsApp_pais" ("id_pais") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS CaosNewsApp_noticia_new;"
        ),

        # Copy data from old table to new table
        migrations.RunSQL(
            """
            INSERT INTO "CaosNewsApp_noticia_new"
            SELECT * FROM "CaosNewsApp_noticia";
            """,
            reverse_sql=""
        ),

        # Drop the old table
        migrations.RunSQL(
            "DROP TABLE \"CaosNewsApp_noticia\";",
            reverse_sql=""
        ),

        # Rename the new table
        migrations.RunSQL(
            "ALTER TABLE \"CaosNewsApp_noticia_new\" RENAME TO \"CaosNewsApp_noticia\";",
            reverse_sql=""
        ),

        # Recreate indexes
        migrations.RunSQL(
            """
            CREATE INDEX "CaosNewsApp_noticia_id_categoria_fbc23f33" ON "CaosNewsApp_noticia" ("id_categoria");
            CREATE INDEX "CaosNewsApp_noticia_id_usuario_4cd5a3f4" ON "CaosNewsApp_noticia" ("id_usuario");
            CREATE INDEX "CaosNewsApp_noticia_id_pais_174b1146" ON "CaosNewsApp_noticia" ("id_pais");
            """,
            reverse_sql=""
        ),

        # Re-enable foreign keys
        migrations.RunSQL(
            "PRAGMA foreign_keys=ON;",
            reverse_sql="PRAGMA foreign_keys=OFF;"
        ),
    ]
