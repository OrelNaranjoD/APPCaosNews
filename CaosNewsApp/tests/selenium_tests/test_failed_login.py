"""
Prueba de fallo de inicio de sesión con Selenium
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..test_constants import TEST_PASSWORDS, QA_USER_CREDENTIALS


class TestFailedLogin:
    """Prueba de fallo de inicio de sesión"""

    @pytest.mark.django_db
    def test_failed_login(self, live_server_url, create_test_user, create_sample_news, browser):
        """Test de fallo de inicio de sesión con credenciales incorrectas"""

        # El usuario ya es creado por el fixture create_test_user
        print(f"✅ Usuario de prueba creado: {create_test_user.username}")

        # Las noticias ya son creadas por el fixture create_sample_news
        print(f"✅ Se crearon {len(create_sample_news)} noticias de ejemplo")

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

        # Llenar formulario con credenciales incorrectas
        print("✍️ Llenando campo de email con credenciales incorrectas")
        username_field = driver.find_element(By.ID, "id_identifier")
        username_field.clear()
        username_field.send_keys(QA_USER_CREDENTIALS['admin']['email'])  # Usuario existente pero contraseña incorrecta
        time.sleep(1)  # Pausa para visualización

        print("🔒 Llenando campo de contraseña incorrecta")
        password_field = driver.find_element(By.ID, "id_password")
        password_field.clear()
        password_field.send_keys(TEST_PASSWORDS['invalid_password'])  # Contraseña incorrecta desde constantes
        time.sleep(1)  # Pausa para visualización

        # Enviar formulario
        print("🚀 Enviando formulario de login con credenciales incorrectas")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and text()='Iniciar Sesión']")
        submit_button.click()
        time.sleep(2)  # Pausa para ver el resultado

        # Verificar que el login falló - debe mostrar error o mantener el modal visible
        print("🔍 Verificando que el login falló...")

        # El modal debe seguir visible porque hubo error
        modal = driver.find_element(By.ID, "login")
        assert modal.is_displayed(), "El modal de login debería seguir visible después de credenciales incorrectas"

        # Verificar que no hay redirección al admin
        current_url = driver.current_url
        assert "/admin/" not in current_url, f"No debería redirigir al admin con credenciales incorrectas. URL actual: {current_url}"

        # Verificar que no aparece enlace de logout (señal de login exitoso)
        logout_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/logout')]")
        assert len(logout_links) == 0, "No debería aparecer enlace de logout con credenciales incorrectas"

        print("✅ Test de fallo de login completado exitosamente - el login falló correctamente")

        # Pausa final para visualizar el resultado
        time.sleep(2)
        print("✅ Test de fallo de login completado")
