"""
Pruebas de creación de noticias con Selenium
"""
import pytest
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestCreateNews:
    """Pruebas de creación de noticias de CaosNews App"""

    @pytest.mark.usefixtures("screenshots_dir", "handle_test_screenshots", "wait_for_element", "click_when_ready", "wait_for_modal_close", "populate_categories_and_countries")
    def test_create_news(self, authenticated_journalist_browser, test_server_url, wait_for_element, click_when_ready, wait_for_modal_close):
        """Test de creación de una noticia usando un usuario periodista con sesión automática"""

        browser = authenticated_journalist_browser
        print("Iniciando prueba de creación de noticias con usuario periodista (sesión automática)")

        # Verificar que el navegador ya tiene la sesión iniciada
        print("✅ Sesión de periodista ya iniciada automáticamente")

        # Navegar directamente a la página de administración
        browser.get(f"{test_server_url}/admin/")

        # Ir a la página de creación de noticias
        crear_noticia_link = wait_for_element(browser, By.XPATH, "//a[@href='/admin/noticias/crear/']")
        assert crear_noticia_link is not None, "No se encontró el enlace para crear noticia"
        crear_noticia_link.click()

        print("Navegando a la página de creación de noticias")

        # Verificar que estamos en la página de creación de noticias
        WebDriverWait(browser, 10).until(
            lambda driver: "crear" in driver.current_url.lower()
        )

        # Asegurarse de que el formulario esté visible antes de interactuar
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "titulo_noticia")))

        print("Formulario de creación de noticias visible")

        # Llenar el formulario de creación de noticias
        title_field = wait_for_element(browser, By.ID, "titulo_noticia")
        assert title_field is not None, "El campo de título no apareció"
        title_field.clear()
        title_field.send_keys("Noticia de prueba - Selenium")
        print("Campo título llenado")

        body_field = wait_for_element(browser, By.ID, "cuerpo_noticia")
        assert body_field is not None, "El campo de cuerpo no apareció"
        body_field.clear()
        body_field.send_keys("Este es el cuerpo de la noticia de prueba creada por Selenium con un usuario periodista.")
        print("Campo cuerpo llenado")

        # Seleccionar categoría
        category_field = wait_for_element(browser, By.ID, "id_categoria")
        assert category_field is not None, "El campo de categoría no apareció"

        # Crear una categoría de prueba si no existe
        from CaosNewsApp.models import Categoria
        categoria_test, _ = Categoria.objects.get_or_create(nombre_categoria="Deportes")

        # Verificar qué opciones están disponibles en el select
        from selenium.webdriver.support.ui import Select
        select_categoria = Select(category_field)
        options = [option.text for option in select_categoria.options]
        print(f"Opciones disponibles en categoría: {options}")

        # Seleccionar la categoría creada o la primera opción disponible (que no sea vacía)
        try:
            select_categoria.select_by_visible_text("Deportes")
            print("Campo categoría seleccionado: Deportes")
        except Exception as e:
            print(f"No se pudo seleccionar 'Deportes': {e}")
            # Intentar seleccionar la primera opción que no esté vacía
            for option in select_categoria.options:
                if option.text.strip() and option.text.strip() != "---------":
                    select_categoria.select_by_visible_text(option.text)
                    print(f"Campo categoría seleccionado: {option.text}")
                    break

        # Seleccionar país
        country_field = wait_for_element(browser, By.ID, "id_pais")
        assert country_field is not None, "El campo de país no apareció"

        # Crear un país de prueba si no existe
        from CaosNewsApp.models import Pais
        pais_test, _ = Pais.objects.get_or_create(pais="Chile")

        # Verificar qué opciones están disponibles en el select de país
        select_pais = Select(country_field)
        country_options = [option.text for option in select_pais.options]
        print(f"Opciones disponibles en país: {country_options}")

        try:
            select_pais.select_by_visible_text("Chile")
            print("Campo país seleccionado: Chile")
        except Exception as e:
            print(f"No se pudo seleccionar 'Chile': {e}")
            # Intentar seleccionar la primera opción que no esté vacía
            for option in select_pais.options:
                if option.text.strip() and option.text.strip() != "---------":
                    select_pais.select_by_visible_text(option.text)
                    print(f"Campo país seleccionado: {option.text}")
                    break

        # Marcar como destacada (opcional)
        destacada_field = wait_for_element(browser, By.ID, "id_destacada")
        if destacada_field is not None:
            destacada_field.click()
            print("Noticia marcada como destacada")

        # Crear una imagen temporal
        image_path = os.path.join(os.path.dirname(__file__), "temp_test_image.jpg")
        with open(image_path, "wb") as img:
            img.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\xda\x63\x60\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82")
        print("Imagen temporal creada")

        # Desplazar hacia el campo de imagen después de seleccionar el país
        image_field = wait_for_element(browser, By.ID, "imagenes")
        assert image_field is not None, "El campo de imágenes no apareció"
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", image_field)
        print("Página desplazada hacia el campo de imagen después de seleccionar el país")

        # Verificar que el campo de imagen está visible
        assert image_field.is_displayed(), "El campo de imagen no está visible después del desplazamiento"

        # Cargar la imagen temporal
        image_field.send_keys(image_path)
        print("Imagen cargada correctamente")

        # Definir y desplazar hacia el botón de guardar
        save_button = wait_for_element(browser, By.XPATH, "//button[@type='submit' and contains(text(), 'Guardar')]")
        assert save_button is not None, "El botón de guardar no apareció"
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        print("Página desplazada hacia el botón de guardar")

        # Verificar que el botón de guardar está visible
        assert save_button.is_displayed(), "El botón de guardar no está visible después del desplazamiento"

        # Hacer clic en el botón de guardar
        save_button.click()

        print("Haciendo clic en el botón de guardar")

        # Eliminar la imagen temporal después de usarla
        if os.path.exists(image_path):
            os.remove(image_path)
            print("Imagen temporal eliminada")

        # Esperar a que la página se redirija o muestre confirmación
        time.sleep(2)

        # Verificar que la noticia fue creada exitosamente
        # Esto puede variar dependiendo de cómo maneje la aplicación la respuesta
        try:
            # Buscar mensaje de éxito
            success_message = wait_for_element(browser, By.XPATH, "//div[contains(@class, 'alert') and contains(text(), 'exitosamente')]", timeout=5)
            if success_message:
                print("✅ Mensaje de éxito encontrado")
            else:
                # Si no hay mensaje de éxito, verificar que estamos en la lista de noticias
                if "noticias" in browser.current_url.lower():
                    print("✅ Redirigido a la lista de noticias")
                else:
                    print(f"URL actual: {browser.current_url}")
                    print(f"Título de página: {browser.title}")

        except TimeoutException:
            # Verificar si estamos en la página de lista de noticias (redirección exitosa)
            if "noticias" in browser.current_url.lower():
                print("✅ Noticia creada exitosamente - redirigido a lista de noticias")
            else:
                print(f"⚠️ No se encontró mensaje de confirmación. URL actual: {browser.current_url}")

        # Verificar que la noticia aparece en la base de datos
        from CaosNewsApp.models import Noticia
        noticias_creadas = Noticia.objects.filter(titulo_noticia="Noticia de prueba - Selenium")
        assert noticias_creadas.count() > 0, "La noticia no fue creada en la base de datos"

        noticia_creada = noticias_creadas.first()
        assert noticia_creada.id_usuario.username == "journalist", "La noticia no fue asignada al usuario periodista correcto"

        print(f"✅ Noticia creada exitosamente con ID: {noticia_creada.id_noticia}")

        # Captura de pantalla final
        browser.save_screenshot("test_create_news_success.png")
