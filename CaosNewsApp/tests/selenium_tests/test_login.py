"""
Pruebas de inicio de sesión con Selenium
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestLogin:
    """Pruebas de inicio de sesión de CaosNews App"""

    @pytest.mark.usefixtures("browser", "screenshots_dir", "handle_test_screenshots", "wait_for_element", "click_when_ready", "wait_for_modal_close")
    def test_successful_login(self, browser, create_test_user, test_server_url, wait_for_element, click_when_ready, wait_for_modal_close):
        """Test de inicio de sesión exitoso"""
        # Navegar a la página principal y validar que el servidor de pruebas está levantado
        browser.get(test_server_url)  # test_server_url debería ser proporcionado por el fixture live_server
        assert "Caos News, La voz de todos." in browser.title, "El servidor de pruebas no está levantado o la página no cargó correctamente"

        # Hacer clic en el enlace de inicio de sesión
        login_link = wait_for_element(browser, By.XPATH, "//a[@data-bs-target='#login']")
        assert login_link is not None, "El enlace de inicio de sesión no apareció"
        login_link.click()

        # Esperar a que aparezca el modal de login
        modal = wait_for_element(browser, By.ID, "login")
        assert modal is not None, "El modal de login no apareció"

        # Ingresar credenciales
        username_field = wait_for_element(browser, By.ID, "id_identifier")
        assert username_field is not None, "El campo de nombre de usuario no apareció"

        # Asegurarse de que el campo de nombre de usuario sea interactuable
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "id_identifier")))

        username_field.clear()
        username_field.send_keys("test@test.cl")
        assert username_field.get_attribute("value") == "test@test.cl", "El campo de nombre de usuario no se llenó correctamente"

        password_field = wait_for_element(browser, By.ID, "id_password")
        assert password_field is not None, "El campo de contraseña no apareció"
        password_field.clear()
        password_field.send_keys("test2025")
        assert password_field.get_attribute("value") == "test2025", "El campo de contraseña no se llenó correctamente"

        # Hacer clic en el botón de inicio de sesión
        submit_button = wait_for_element(browser, By.XPATH, "//input[@type='submit' and @value='Iniciar Sesión']")
        assert submit_button is not None, "El botón de inicio de sesión no apareció"
        submit_button.click()

        # Confirmar mensaje de sesión correcta en el modal
        success_message = wait_for_element(browser, By.XPATH, "//div[@id='successAlert' and contains(text(), 'Inicio de sesión exitoso.')]")
        assert success_message is not None, "No se mostró mensaje de éxito"

        # Esperar a que el modal se cierre
        modal_closed = wait_for_modal_close(browser, "login")
        assert modal_closed, "El modal de login no se cerró automáticamente"

        # Presionar el enlace Panel de control del header
        panel_control = wait_for_element(browser, By.XPATH, "//a[@href='/admin/' and contains(text(), 'Panel de control')]")
        assert panel_control is not None, "No se encontró el enlace al Panel de Control"
        panel_control.click()

        # Dentro del panel presionar cerrar sesión
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Hacer scroll hasta el final de la página
        time.sleep(1)  # Dar tiempo para que el scroll se complete
        logout_link = wait_for_element(browser, By.XPATH, "//a[contains(@href, '/logout')]")
        assert logout_link is not None, "No se encontró el enlace de cerrar sesión después del scroll"

        # Asegurarse de que el enlace de cerrar sesión sea visible y clicable
        browser.execute_script("arguments[0].scrollIntoView(true);", logout_link)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]")))

        logout_link.click()

        # Comprobar que aparece nuevamente el enlace para iniciar sesión en el header
        login_link = wait_for_element(browser, By.XPATH, "//a[@data-bs-target='#login']")
        assert login_link is not None, "No se muestra el enlace de inicio de sesión después de cerrar sesión"

        # Captura de pantalla final
        browser.save_screenshot("test_successful_login_2_logout.png")
