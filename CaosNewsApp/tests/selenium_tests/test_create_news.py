"""Test RF-3-01: Crear noticia (versión simplificada)"""

import pytest
import time
import os
from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class TestRF301CrearNoticia:
    """Test RF-3-01: Crear noticia"""

    @pytest.mark.django_db
    def test_create_news(
        self,
        test_server_url,
        create_test_journalist,
        authenticated_journalist_browser,
    ):
        """Test que verifica la creación de una noticia por un periodista"""
        driver = authenticated_journalist_browser

        print("🧪 Test RF-3-01: Crear noticia")

        # 1. Navegar a creación de noticias
        print("1. Navegando a página de creación...")
        driver.get(f"{test_server_url}/admin/noticias/crear/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "titulo_noticia"))
        )

        # 2. Llenar formulario
        print("2. Llenando formulario...")
        driver.find_element(By.ID, "titulo_noticia").send_keys(
            "Recta final de los Premios Regionales de Aysén 2023"
        )
        time.sleep(1)

        cuerpo_noticia = """Este 31 de julio se agota el plazo para que instituciones, tales como universidades, establecimientos educacionales, municipalidades, agrupaciones culturales o sociales, corporaciones o fundaciones de la Región de Aysén o de otras regiones del país puedan postular nombres a los Premios Regionales de Arte, Cultura y Patrimonio 2023. Este año, el certamen organizado por las Seremi de Culturas Aysén está dedicado a la literatura y premiará las categorías Narrativa, Poesía y Ensayo."""
        driver.find_element(By.ID, "cuerpo_noticia").send_keys(cuerpo_noticia)
        time.sleep(1)

        # 3. Seleccionar categoría
        print("3. Seleccionando categoría...")
        Select(driver.find_element(By.ID, "id_categoria")).select_by_visible_text(
            "Cultura"
        )
        time.sleep(1)

        # 4. Seleccionar país
        print("4. Seleccionando país...")
        Select(driver.find_element(By.ID, "id_pais")).select_by_visible_text("Chile")
        time.sleep(1)

        # 5. Adjuntar imagen
        print("5. Adjuntando imagen...")
        imagen_path = os.path.join(settings.MEDIA_ROOT, "news", "25.jpg")
        driver.find_element(By.ID, "imagenes").send_keys(imagen_path)
        time.sleep(1)

        # 6. Guardar
        print("6. Enviando formulario...")
        url_inicial = driver.current_url

        # Buscar botón submit
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        print(f"   Botón encontrado: '{submit_btn.text}'")

        # Hacer clic
        submit_btn.click()
        print("   Clic realizado")

        # Esperar redirección o procesamiento
        time.sleep(3)

        url_final = driver.current_url
        print(f"   URL inicial: {url_inicial}")
        print(f"   URL final: {url_final}")

        # 7. Verificar creación exitosa
        print("7. Verificando creación exitosa...")

        # Verificación 1: La URL cambió a la página de borradores (indica éxito)
        assert "/admin/noticias/borradores/" in url_final, f"La redirección no fue correcta. URL final: {url_final}"
        print("   ✅ Redirección exitosa a borradores")

        # Verificación 2: Buscar la noticia en la página de borradores
        print("   Verificando que la noticia aparece en la lista de borradores...")
        try:
            # Buscar el título de la noticia en la página actual
            titulo_noticia = "Recta final de los Premios Regionales de Aysén 2023"
            noticia_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{titulo_noticia}')]"))
            )
            print("   ✅ Noticia encontrada en la lista de borradores")

            # Verificación 3: Comprobar que está en la tabla de borradores
            tabla_borradores = driver.find_element(By.CLASS_NAME, "table-striped")
            assert titulo_noticia in tabla_borradores.text, "La noticia no está visible en la tabla de borradores"
            print("   ✅ Noticia visible en la tabla de borradores")

        except Exception as e:
            print(f"   ❌ Error verificando la noticia en la interfaz: {e}")
            # Intentar obtener el contenido de la página para debug
            page_content = driver.page_source
            if titulo_noticia in page_content:
                print("   ℹ️  La noticia SÍ está en el HTML de la página")
            else:
                print("   ❌ La noticia NO está en el HTML de la página")
            raise AssertionError(f"No se pudo verificar la creación de la noticia: {e}")

        print("   ✅ Noticia creada y verificada exitosamente")
