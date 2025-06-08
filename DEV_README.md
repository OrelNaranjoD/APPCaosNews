# Entorno de Desarrollo - CaosNews

## Configuración Automática

Para configurar el entorno de desarrollo con datos de prueba, simplemente ejecuta:

```powershell
.\scripts\run_dev_server.ps1
```

O alternativamente, usa el comando personalizado:

```bash
python manage.py setup_dev
```

## Datos de Prueba Disponibles

### Usuarios
Los siguientes usuarios están disponibles en el entorno de desarrollo:

#### Usuarios de Fixtures (desde test_data.json)
- **testuser** (test@caosnews.com)
  - Usuario normal
  - Contraseña: Ver hash en fixtures

- **admin** (admin@caosnews.com)
  - Superusuario y staff
  - Contraseña: Ver hash en fixtures

#### Usuario de Desarrollo
- **devadmin** (devadmin@caosnews.com)
  - Superusuario de desarrollo
  - Contraseña: `devpass123`

### Contenido
- **3 Noticias** de prueba en diferentes categorías
- **3 Categorías**: Tecnología, Deportes, Política
- **2 Países**: Chile, Argentina

## Comandos Útiles

### Configurar entorno de desarrollo
```bash
# Configuración completa
python manage.py setup_dev

# Resetear y configurar desde cero
python manage.py setup_dev --reset

# Configurar sin cargar fixtures
python manage.py setup_dev --no-fixtures
```

### Cargar solo fixtures
```bash
python manage.py loaddata CaosNewsApp/fixtures/test_data.json
```

### Verificar datos cargados
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from CaosNewsApp.models import Noticia, Categoria, Pais
print(f'Usuarios: {User.objects.count()}')
print(f'Noticias: {Noticia.objects.count()}')
print(f'Categorías: {Categoria.objects.count()}')
print(f'Países: {Pais.objects.count()}')
"
```

## Acceso al Sitio

Una vez que el servidor esté ejecutándose:

- **Sitio principal**: http://127.0.0.1:8000
- **Panel de administración**: http://127.0.0.1:8000/adminDJango/
  - Usuario: `devadmin`
  - Contraseña: `devpass123`

## Base de Datos

El entorno de desarrollo usa una base de datos SQLite separada:
- **Archivo**: `db_dev.sqlite3`
- **Ubicación**: Raíz del proyecto

## Notas

- Los datos de prueba se cargan automáticamente cada vez que ejecutas el script de desarrollo
- Si necesitas resetear completamente los datos, usa el comando `setup_dev --reset`
- Las contraseñas de los usuarios de fixtures están hasheadas en el archivo JSON
- Para desarrollo diario, usa el usuario `devadmin` con contraseña simple
