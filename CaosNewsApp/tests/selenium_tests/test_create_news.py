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
        live_server,
        create_test_journalist,
        authenticated_journalist_browser,
        populate_categories_and_countries,
    ):
        """Test que verifica la creación de una noticia por un periodista"""
        driver = authenticated_journalist_browser

        print("🧪 Test RF-3-01: Crear noticia")

        # 1. Navegar a creación de noticias
        print("1. Navegando a página de creación...")
        driver.get(f"{live_server.url}/admin/noticias/crear/")
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

        # 7. Verificar en base de datos
        print("7. Verificando en base de datos...")
        from CaosNewsApp.models import Noticia

        # Buscar noticia creada
        noticia = Noticia.objects.filter(
            titulo_noticia="Recta final de los Premios Regionales de Aysén 2023"
        ).first()
        assert noticia is not None, "La noticia no fue creada correctamente"
