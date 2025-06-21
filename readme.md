# Guía de instalación y ejecución de la aplicación CaosNews

Sigue los siguientes pasos para configurar y ejecutar la aplicación CaosNews en tu entorno local.

## Requisitos previos

Asegúrate de tener instalados los siguientes programas antes de comenzar:

- [Python 3.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

## Configuración del entorno virtual

1. **Clona el repositorio**: Clona el repositorio de CaosNews desde GitHub.

    ```bash
    git clone https://github.com/OrelNaranjo/APPCaosNews.git
    ```

2. **Crea el entorno virtual**: Utiliza el siguiente comando para crear un entorno virtual en Python.

    ```bash
    python -m venv venv
    ```

3. **Activa el entorno virtual**:

    - En Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - En macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4. **Instala las dependencias**: Ejecuta el siguiente comando para instalar todas las dependencias necesarias.

    ```bash
    pip install -r requirements.txt
    ```

## Ejecución de la aplicación

1. **Ejecuta la aplicación**: Utiliza el siguiente comando para iniciar el servidor de desarrollo de Django.

    ```bash
    python manage.py runserver
    ```

2. **Accede a la aplicación**: Una vez que el servidor esté en funcionamiento, puedes acceder a la aplicación navegando a la siguiente dirección en tu navegador web:

    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Crear un superusuario (opcional)

Para acceder al panel de administración de Django, necesitas crear un superusuario. Ejecuta el siguiente comando y sigue las instrucciones:

```bash
python manage.py createsuperuser
```

Para ejecutar Sonar Scanner

```bash
C:\SonarQube\sonar-scanner\bin\sonar-scanner.bat
```

## Sistema de Notificaciones de Suscripción

### Funcionalidad de Notificaciones

El sistema incluye un watcher manual para revisar suscripciones próximas a vencer y enviar notificaciones por email.

### Ejecución Manual

```powershell
# Revisar suscripciones próximas a vencer (3 días por defecto)
.\scripts\check_subscriptions_manual.ps1

# Modo prueba (no envía emails reales)
.\scripts\check_subscriptions_manual.ps1 -DryRun

# Revisar solo próximo día
.\scripts\check_subscriptions_manual.ps1 -Dias 1

# Ver ayuda completa
.\scripts\check_subscriptions_manual.ps1 -Help
```
