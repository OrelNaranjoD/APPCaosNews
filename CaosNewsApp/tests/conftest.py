import pytest
import os
import time
import sys
import socket
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from django.contrib.auth import get_user_model

# Configuración del servidor QA
QA_SERVER_URL = "http://127.0.0.1:8001"

User = get_user_model()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from .test_constants import TEST_USER_CREDENTIALS, QA_USER_CREDENTIALS


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture
def create_test_user(db):
    """Fixture para crear un usuario de prueba administrador"""
    user = User.objects.create_user(
        username=TEST_USER_CREDENTIALS['username'],
        email=TEST_USER_CREDENTIALS['email'],
        password=TEST_USER_CREDENTIALS['password'],  # Django hashea automáticamente
        first_name=TEST_USER_CREDENTIALS['first_name'],
        last_name=TEST_USER_CREDENTIALS['last_name'],
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    from django.contrib.auth.models import Group

    admin_group, _ = Group.objects.get_or_create(name="Administrador")
    user.groups.add(admin_group)

    return user


@pytest.fixture
def create_test_journalist(db):
    """Fixture para obtener o crear un usuario periodista"""
    from django.contrib.auth.models import Group

    # Para pruebas con servidor QA, usar credenciales QA
    qa_creds = QA_USER_CREDENTIALS['periodista']

    try:
        # Intentar obtener el usuario QA existente
        journalist_user = User.objects.get(username=qa_creds['username'])
        print(f"✅ Usuario QA periodista encontrado: {journalist_user.username}")
    except User.DoesNotExist:
        # Si no existe (en tests unitarios), crear uno temporal
        journalist_user = User.objects.create_user(
            username=qa_creds['username'],
            email=qa_creds['email'],
            password=qa_creds['password'],
            first_name=qa_creds['first_name'],
            last_name=qa_creds['last_name'],
        )
        journalist_user.is_staff = True

        # Añadir al grupo Periodista
        periodista_group, _ = Group.objects.get_or_create(name="Periodista")
        journalist_user.groups.add(periodista_group)
        journalist_user.save()
        print(f"✅ Usuario periodista creado temporalmente: {journalist_user.username}")

    return journalist_user


@pytest.fixture
def authenticated_journalist_browser(browser, create_test_journalist, test_server_url):
    """Fixture que proporciona un navegador con sesión de periodista ya iniciada"""

    # Usar el servidor QA externo
    base_url = test_server_url
    login_url = f"{base_url}/adminDJango/login/?next=/admin/noticias/crear/"
    print(f"🔐 Iniciando sesión en el servidor QA: {login_url}")
    browser.get(login_url)

    try:
        # Esperar el campo de username
        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Llenar credenciales (usar credenciales de QA)
        qa_creds = QA_USER_CREDENTIALS['periodista']
        username_field.send_keys(qa_creds['username'])

        password_field = browser.find_element(By.NAME, "password")
        password_field.send_keys(qa_creds['password'])

        # Hacer clic en el botón de login
        login_button = browser.find_element(By.XPATH, "//input[@type='submit']")
        login_button.click()

        # Esperar redirección exitosa
        WebDriverWait(browser, 10).until(
            lambda driver: "/admin/noticias/crear/" in driver.current_url or "/admin/" in driver.current_url
        )

        # Debug: Verificar la URL actual y título de la página
        print(f"📍 URL después del login: {browser.current_url}")
        print(f"📝 Título de página: {browser.title}")

        # Verificar si necesitamos navegar manualmente a la página de creación
        if "/admin/noticias/crear/" not in browser.current_url:
            print("🔄 Navegando manualmente a la página de creación de noticias...")
            browser.get(f"{base_url}/admin/noticias/crear/")
            # Esperar a que la página cargue
            time.sleep(2)
            print(f"📍 URL después de navegación manual: {browser.current_url}")

        print("✅ Sesión de periodista iniciada correctamente en servidor QA")

    except Exception as auth_error:
        print(f"❌ Error al iniciar sesión: {auth_error}")
        print(f"URL actual: {browser.current_url}")
        print(f"Título de página: {browser.title}")
        raise

    return browser


@pytest.fixture
def create_test_news(db, create_test_user):
    """Fixture para crear una noticia de prueba"""
    from CaosNewsApp.models import Categoria, Pais, Noticia, DetalleNoticia

    cat, _ = Categoria.objects.get_or_create(nombre_categoria="Deportes")

    pais, _ = Pais.objects.get_or_create(pais="Chile")

    noticia = Noticia.objects.create(
        titulo_noticia="Noticia de prueba",
        cuerpo_noticia="Contenido de prueba para edición",
        id_categoria=cat,
        id_pais=pais,
        id_usuario=create_test_user,
        destacada=False,
        activo=True,
    )

    detalle = DetalleNoticia.objects.get(noticia=noticia)
    detalle.estado = None
    detalle.publicada = True
    detalle.save()

    print(f"✅ Noticia de prueba creada con ID: {noticia.id_noticia}")

    return noticia


@pytest.fixture
def create_sample_news(db, create_test_user):
    """Fixture para crear una noticia destacada específica con imagen para las pruebas"""
    from CaosNewsApp.models import (
        Noticia,
        DetalleNoticia,
        Categoria,
        Pais,
        ImagenNoticia,
    )
    from django.conf import settings

    print("\n=== CREANDO NOTICIA DESTACADA PARA TESTS ===")

    # Crear o recuperar la categoría Cultura
    categoria, _ = Categoria.objects.get_or_create(nombre_categoria="Cultura")

    # Crear o recuperar el país Chile
    pais, _ = Pais.objects.get_or_create(pais="Chile")

    # Crear una noticia con datos reales
    noticia = Noticia.objects.create(
        titulo_noticia="Recta final de los Premios Regionales de Aysén 2023",
        cuerpo_noticia="""Este 31 de julio se agota el plazo para que instituciones, tales como universidades, establecimientos educacionales, municipalidades, agrupaciones culturales o sociales, corporaciones o fundaciones de la Región de Aysén o de otras regiones del país puedan postular nombres a los Premios Regionales de Arte, Cultura y Patrimonio 2023. Este año, el certamen organizado por las Seremi de Culturas Aysén está dedicado a la literatura y premiará las categorías Narrativa, Poesía y Ensayo. El objetivo de estos premios es poner en valor la obra literaria de chilenas y chilenos nacidos o no en la Región de Aysén, que a través de sus obras han fortalecido la identidad cultural y han aportado a la descentralización del desarrollo artístico y cultural. El seremi de Culturas Aysén, Felipe Quiroz, cree que se trata "de una oportunidad que fortalece la creación literaria regional y que profundiza la imagen de Aysén como un territorio creativo. Este premio viene a reforzar el compromiso del Gobierno en materia del libro y fomento lector. Como ministerio queremos premiar obras que nos identifiquen como territorio y para eso invitamos a organismos públicos y privados a presentar sus nombres para postular a los Premios Regionales 2023". Las y los ganadores de cada categoría recibirán como premio un estímulo monetario equivalente a $1.700.000, además de la estatuilla "Témpano", creada por la artista visual Paz Schwencke, tras un concurso era que resultó elegida. El jurado está compuesto por el Seremi de Culturas Aysén o quien él designe; la o el Encargado Nacional del Área de Libro y lectura del Ministerio de las Culturas, las Artes y el Patrimonio; la Coordinadora Regional de la Unidad de Fomento de la Cultura y las Artes de la Seremi de las Culturas, las Artes y el Patrimonio o quien ella designe en su representación; la encargada de la Biblioteca Regional de Aysén o a quien ella designe en su representación; y el escritor regional Eleodoro Sanhueza, ganador del Premio Regional de Arte y Cultura año 2014.""",
        id_categoria=categoria,
        id_pais=pais,
        id_usuario=create_test_user,
        destacada=False,
        activo=True,
        eliminado=False,
    )

    detalle = DetalleNoticia.objects.get(noticia=noticia)
    detalle.estado = "A"  # Aprobado
    detalle.publicada = True
    detalle.save()


    imagen_path = os.path.join(settings.MEDIA_ROOT, "news", "25.jpg")

    if os.path.exists(imagen_path):
        imagen = ImagenNoticia.objects.create(noticia=noticia)
        imagen.imagen.name = "news/25.jpg"
        imagen.save()

    else:
        print(f"❌ Creando noticia sin imagen")


    return [
        noticia
    ]


@pytest.fixture
def browser():
    """Fixture para configurar y proporcionar el navegador Edge optimizado para pruebas"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    webdriver_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "drivers", "msedgedriver.exe")
    )
    service = Service(webdriver_path)
    service.log_path = os.devnull

    driver = webdriver.Edge(service=service, options=options)
    driver.implicitly_wait(1)
    yield driver
    driver.quit()


@pytest.fixture
def wait_helpers():
    """
    Fixture que proporciona funciones de utilidad para esperar explícitamente
    condiciones en el navegador.
    """

    def wait_for_element_presence(driver, by, locator, timeout=10):
        """Espera hasta que un elemento esté presente en el DOM."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            return element
        except TimeoutException:
            return None

    def wait_for_element_visibility(driver, by, locator, timeout=10):
        """Espera hasta que un elemento esté visible en la página."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return element
        except TimeoutException:
            return None

    def wait_for_text_in_element(driver, by, locator, text, timeout=10):
        """Espera hasta que un texto específico esté presente en un elemento."""
        try:
            WebDriverWait(driver, timeout).until(
                EC.text_to_be_present_in_element((by, locator), text)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_error_message(driver, timeout=10):
        """Espera hasta que aparezca un mensaje de error en el contenedor de errores."""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: len(d.find_element(By.ID, "messageContainer").text.strip())
                > 0
            )
            return driver.find_element(By.ID, "messageContainer").text
        except TimeoutException:
            return None
        except Exception as e:
            print(f"Error al buscar mensaje de error: {str(e)}")
            return None

    def wait_for_success_message(driver, timeout=10):
        """Espera hasta que aparezca un mensaje de éxito en el contenedor de mensajes."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                message_container = driver.find_element(By.ID, "messageContainer")
                text = message_container.text.strip()
                if len(text) > 0 and (
                    "exitoso" in text.lower()
                    or "éxito" in text.lower()
                    or "bienvenido" in text.lower()
                ):
                    print(f"Mensaje de éxito encontrado: '{text}'")
                    return text
            except Exception as e:
                pass
            time.sleep(0.5)
        try:
            message_container = driver.find_element(By.ID, "messageContainer")
            text = message_container.text.strip()
            if len(text) > 0:
                print(
                    f"Contenido del messageContainer (no reconocido como éxito): '{text}'"
                )
        except:
            pass

        return None

    def wait_for_url_contains(driver, text, timeout=10):
        """Espera hasta que la URL contenga un texto específico."""
        try:
            WebDriverWait(driver, timeout).until(EC.url_contains(text))
            return True
        except TimeoutException:
            return False

    def wait_for_input_value(driver, by, locator, expected_value, timeout=10):
        """Espera hasta que un campo de entrada tenga un valor específico."""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.find_element(by, locator).get_attribute("value")
                == expected_value
            )
            return True
        except TimeoutException:
            return False
        except Exception as e:
            print(f"Error al esperar valor de input: {str(e)}")
            return False

    def fill_input_field(driver, by, locator, value, timeout=10):
        """Llena un campo de entrada con un valor específico, asegurando que se complete correctamente."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                field = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
                field.clear()
                field.send_keys(value)
                time.sleep(0.5)

                actual_value = field.get_attribute("value")
                if actual_value == value:
                    return True
                else:
                    print(
                        f"Intento {attempt+1}: El valor ingresado no coincide. Esperado: '{value}', Actual: '{actual_value}'"
                    )
            except Exception as e:
                print(f"Error en intento {attempt+1} al llenar campo: {str(e)}")

        return False

    return {
        "wait_for_element_presence": wait_for_element_presence,
        "wait_for_element_visibility": wait_for_element_visibility,
        "wait_for_text_in_element": wait_for_text_in_element,
        "wait_for_error_message": wait_for_error_message,
        "wait_for_success_message": wait_for_success_message,
        "wait_for_url_contains": wait_for_url_contains,
        "wait_for_input_value": wait_for_input_value,
        "fill_input_field": fill_input_field,
    }


# Se movieron las utilidades wait_for_element, click_when_ready y wait_for_modal_close al fichero de configuración
@pytest.fixture(scope="function")
def wait_for_element():
    def _wait_for_element(browser, locator_type, locator, timeout=10):
        try:
            element = WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((locator_type, locator))
            )
            return element
        except TimeoutException:
            print(
                f"El elemento con locator {locator} no fue encontrado en {timeout} segundos"
            )
            return None

    return _wait_for_element


@pytest.fixture(scope="function")
def click_when_ready(wait_for_element):
    def _click_when_ready(browser, locator_type, locator, timeout=10):
        element = wait_for_element(browser, locator_type, locator, timeout)
        if element and element.is_displayed():
            element.click()
            return True
        return False

    return _click_when_ready


@pytest.fixture(scope="function")
def wait_for_modal_close():
    def _wait_for_modal_close(browser, modal_id, timeout=10):
        try:
            WebDriverWait(browser, timeout).until_not(
                EC.visibility_of_element_located((By.ID, modal_id))
            )
            return True
        except TimeoutException:
            print(f"El modal {modal_id} no se cerró en {timeout} segundos")
            return False

    return _wait_for_modal_close


# Fixture mejorado para servidor de pruebas rápido
@pytest.fixture(scope="session")
def fast_test_server():
    """Servidor de pruebas rápido usando pytest-django live_server optimizado"""
    import socket

    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    print(f"✅ Servidor de pruebas configurado para {base_url}")
    return base_url


@pytest.fixture
def test_server_url():
    """
    Fixture que proporciona la URL del servidor QA externo.
    Este servidor debe estar ejecutándose previamente en http://127.0.0.1:8001
    """
    print(f"🎯 Usando servidor QA externo en {QA_SERVER_URL}")
    return QA_SERVER_URL

@pytest.fixture
def live_server_url():
    """
    Fixture de compatibilidad que mapea al servidor QA.
    Reemplaza el live_server estándar de Django con nuestro servidor QA.
    """
    print(f"🔗 Redirigiendo live_server a servidor QA: {QA_SERVER_URL}")

    # Crear un objeto mock que simule live_server.url
    class MockLiveServer:
        @property
        def url(self):
            return QA_SERVER_URL

    return MockLiveServer()


@pytest.fixture(scope="function")
def populate_categories_and_countries(db):
    """Fixture para poblar las tablas de categorías y países."""
    from CaosNewsApp.models import Categoria, Pais

    # Poblar categorías
    categorias = ["Deportes", "Economía", "Política", "Cultura", "Tecnología"]
    for nombre in categorias:
        Categoria.objects.get_or_create(nombre_categoria=nombre)

    # Poblar países
    paises = ["Chile", "Argentina", "Perú", "Brasil", "México"]
    for nombre in paises:
        Pais.objects.get_or_create(pais=nombre)

    print("✅ Categorías y países poblados correctamente")
