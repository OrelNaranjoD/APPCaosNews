"""
Pruebas de inicio de sesión fallido con Selenium
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestFailedLogin:
    """Pruebas de inicio de sesión fallido de CaosNews App"""

    @pytest.mark.usefixtures("browser", "screenshots_dir", "handle_test_screenshots", "wait_for_element", "click_when_ready", "wait_for_modal_close")
    def test_failed_login(self, browser, test_server_url, wait_for_element, click_when_ready, wait_for_modal_close):
        """Test de inicio de sesión fallido"""
        # Navegar a la página principal
        browser.get(test_server_url)
        assert "Caos News, La voz de todos." in browser.title, "El servidor de pruebas no está levantado o la página no cargó correctamente"

        # Hacer clic en el enlace de inicio de sesión
        login_link = wait_for_element(browser, By.XPATH, "//a[@data-bs-target='#login']")
        assert login_link is not None, "El enlace de inicio de sesión no apareció"
        login_link.click()

        # Esperar a que aparezca el modal de login
        modal = wait_for_element(browser, By.ID, "login")
        assert modal is not None, "El modal de login no apareció"

        # Asegurarse de que el modal sea visible e interactuable
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "login")))

        # Ingresar credenciales incorrectas
        username_field = wait_for_element(browser, By.ID, "id_identifier")
        assert username_field is not None, "El campo de nombre de usuario no apareció"
        username_field.clear()
        username_field.send_keys("wrong@test.cl")
        assert username_field.get_attribute("value") == "wrong@test.cl", "El campo de nombre de usuario no se llenó correctamente"

        password_field = wait_for_element(browser, By.ID, "id_password")
        assert password_field is not None, "El campo de contraseña no apareció"
        password_field.clear()
        password_field.send_keys("wrongpassword")
        assert password_field.get_attribute("value") == "wrongpassword", "El campo de contraseña no se llenó correctamente"

        # Hacer clic en el botón de inicio de sesión
        submit_button = wait_for_element(browser, By.XPATH, "//input[@type='submit' and @value='Iniciar Sesión']")
        assert submit_button is not None, "El botón de inicio de sesión no apareció"
        submit_button.click()

        # Confirmar mensaje de error en el modal
        error_message = wait_for_element(browser, By.XPATH, "//div[contains(@class, 'alert-danger') and (contains(text(), 'Credenciales incorrectas') or contains(text(), 'Correo electrónico o usuario no válido'))]")
        assert error_message is not None, "No se mostró mensaje de error"

        # Captura de pantalla final
        browser.save_screenshot("test_failed_login_error.png")
