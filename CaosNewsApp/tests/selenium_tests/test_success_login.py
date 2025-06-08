"""
Prueba simplificada de inicio de sesión con Selenium
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..test_constants import TEST_USER_CREDENTIALS


class TestSuccessLogin:
    """Prueba RF-2-01 de inicio de sesión exitoso con Selenium"""

    @pytest.mark.django_db
    def test_success_login(self, live_server_url, create_test_user, create_sample_news, browser):
        """Test simplificado de inicio de sesión exitoso usando credenciales del caso de uso"""

        # El usuario ya es creado por el fixture create_test_user (para base de test)
        print(f"✅ Usuario de prueba creado: {create_test_user.username}")

        # Las noticias ya son creadas por el fixture create_sample_news
        print(f"✅ Se crearon {len(create_sample_news)} noticias de ejemplo")

        # Para el login usaremos las credenciales del caso de uso
        print(f"ℹ️ Para login usaremos usuario del caso de uso: {TEST_USER_CREDENTIALS['email']}")

        # Usar el browser del fixture (ya configurado)
        driver = browser

        # Navegar a la página principal
        print(f"Navegando a: {live_server_url.url}")
        driver.get(live_server_url.url)

        # Verificar que la página carga
        assert "Caos News" in driver.title or "Caos" in driver.title
        print("✅ Página principal cargada correctamente")

        # Buscar el enlace de login
        login_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-bs-target='#login']"))
        )
        print("🔍 Haciendo clic en el enlace de login")
        login_link.click()

        # Esperar que aparezca el modal
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login"))
        )
        print("📱 Modal de login apareció")

        # Llenar formulario
        print("✍️ Llenando campo de email")
        username_field = driver.find_element(By.ID, "id_identifier")
        username_field.clear()
        username_field.send_keys(TEST_USER_CREDENTIALS['email'])
        time.sleep(1)  # Pausa para visualización

        print("🔒 Llenando campo de contraseña")
        password_field = driver.find_element(By.ID, "id_password")
        password_field.clear()
        password_field.send_keys(TEST_USER_CREDENTIALS['password'])  # Contraseña en texto plano para el formulario
        time.sleep(1)  # Pausa para visualización

        # Enviar formulario
        print("🚀 Enviando formulario de login")
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Iniciar Sesión']")
        submit_button.click()
        time.sleep(1)  # Pausa más larga para ver el resultado y las noticias

        # Esperar que el login sea exitoso - verificar múltiples indicadores
        print("🔍 Verificando que el login fue exitoso...")

        # Verificar que el modal se cerró (señal de login exitoso)
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "login"))
        )
        print("✅ Modal de login se cerró correctamente")

        # Verificar que aparece enlace de logout (señal clara de estar logueado)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]"))
        )
        print("✅ Enlace de logout detectado - usuario está logueado")

        # Verificar que el enlace de login ya no está visible
        login_links = driver.find_elements(By.XPATH, "//a[@data-bs-target='#login']")
        assert len(login_links) == 0, "El enlace de login no debería estar visible después de un login exitoso"
        print("✅ Enlace de login ya no visible")

        # Verificar que podemos acceder al área de admin si el usuario tiene permisos
        try:
            driver.get(f"{live_server_url.url}/admin/")
            time.sleep(2)
            if "/admin/" in driver.current_url and "login" not in driver.current_url.lower():
                print("✅ Acceso al área de administración confirmado")
            else:
                print("ℹ️ Usuario no tiene acceso al área de administración (normal para usuarios regulares)")
        except Exception as e:
            print(f"ℹ️ No se pudo verificar acceso al admin: {e}")

        print("✅ Test de login exitoso completado satisfactoriamente")
