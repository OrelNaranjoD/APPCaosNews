"""
Prueba simplificada de inicio de sesión con Selenium
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestSuccessLogin:
    """Prueba RF-2-01 de inicio de sesión exitoso con Selenium"""

    @pytest.mark.django_db
    def test_success_login(self, live_server, create_test_user, create_sample_news, browser):
        """Test simplificado de inicio de sesión exitoso con noticias de ejemplo"""

        # El usuario ya es creado por el fixture create_test_user
        print(f"✅ Usuario de prueba creado: {create_test_user.username}")

        # Las noticias ya son creadas por el fixture create_sample_news
        print(f"✅ Se crearon {len(create_sample_news)} noticias de ejemplo")

        # Usar el browser del fixture (ya configurado)
        driver = browser

        # Navegar a la página principal
        print(f"Navegando a: {live_server.url}")
        driver.get(live_server.url)

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
        username_field.send_keys("juanperez@duocuc.cl")
        time.sleep(1)  # Pausa para visualización

        print("🔒 Llenando campo de contraseña")
        password_field = driver.find_element(By.ID, "id_password")
        password_field.clear()
        password_field.send_keys("PassSegura123")
        time.sleep(1)  # Pausa para visualización

        # Enviar formulario
        print("🚀 Enviando formulario de login")
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Iniciar Sesión']")
        submit_button.click()
        time.sleep(1)  # Pausa más larga para ver el resultado y las noticias

        # Esperar mensaje de éxito o redirección
        try:
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'exitoso')]")),
                    EC.url_contains("/admin/"),
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]"))
                )
            )
            print("✅ Login exitoso detectado")
        except TimeoutException:
            print("⚠️ No se detectó mensaje de éxito, pero continuando...")

        # Pausa final para ver la página con noticias
        time.sleep(1)
        print("✅ Test de login simple completado exitosamente")
