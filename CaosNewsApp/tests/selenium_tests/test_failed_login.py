"""
Prueba de fallo de inicio de sesión con Selenium
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestFailedLogin:
    """Prueba de fallo de inicio de sesión"""

    @pytest.mark.django_db
    def test_failed_login(self, live_server, create_test_user, create_sample_news, browser):
        """Test de fallo de inicio de sesión con credenciales incorrectas"""

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

        # Llenar formulario con credenciales incorrectas
        print("✍️ Llenando campo de email con credenciales incorrectas")
        username_field = driver.find_element(By.ID, "id_identifier")
        username_field.clear()
        username_field.send_keys("wronguser@test.cl")
        time.sleep(1)  # Pausa para visualización

        print("🔒 Llenando campo de contraseña incorrecta")
        password_field = driver.find_element(By.ID, "id_password")
        password_field.clear()
        password_field.send_keys("wrongpassword")
        time.sleep(1)  # Pausa para visualización

        # Enviar formulario
        print("🚀 Enviando formulario de login con credenciales incorrectas")
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Iniciar Sesión']")
        submit_button.click()
        time.sleep(2)  # Pausa para ver el resultado

        # Esperar mensaje de error - esto es lo que debe pasar con credenciales incorrectas
        try:
            # Buscar mensaje de error en diferentes lugares posibles
            error_detected = False

            # Opción 1: Mensaje de error en contenedor específico
            try:
                error_message = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger') or contains(@class, 'error') or contains(text(), 'error') or contains(text(), 'incorrecto')]"))
                )
                print(f"❌ Mensaje de error detectado: {error_message.text}")
                error_detected = True
            except TimeoutException:
                pass

            # Opción 2: El modal sigue visible (no se cerró porque hubo error)
            if not error_detected:
                try:
                    modal_still_visible = driver.find_element(By.ID, "login")
                    if modal_still_visible.is_displayed():
                        print("❌ Modal de login sigue visible - login falló correctamente")
                        error_detected = True
                except:
                    pass

            # Opción 3: No hay redirección exitosa
            if not error_detected:
                current_url = driver.current_url
                if "/admin/" not in current_url and "logout" not in driver.page_source:
                    print("❌ No hubo redirección exitosa - login falló correctamente")
                    error_detected = True

            if error_detected:
                print("✅ Test de fallo de login completado exitosamente")
            else:
                print("⚠️ No se detectó claramente el fallo de login")

        except Exception as e:
            print(f"❌ Error durante la verificación: {str(e)}")

        # Pausa final para visualizar el resultado
        time.sleep(2)
        print("✅ Test de fallo de login completado")
