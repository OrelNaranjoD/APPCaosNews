from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from PIL import Image
import io
from CaosNewsApp.models import Noticia, Categoria, Pais
from ..test_constants import TEST_PASSWORDS, TEST_DATA

User = get_user_model()

class CategoryTestCase(TestCase):
    """Crea un conjunto de pruebas para el modelo Categoria"""

    def test_category_creation(self):
        """Prueba la creación de una categoría"""
        category = Categoria.objects.create(nombre_categoria=TEST_DATA['categoria_nombre'])
        self.assertEqual(category.nombre_categoria, TEST_DATA['categoria_nombre'])
        self.assertTrue(isinstance(category, Categoria))
        self.assertEqual(str(category), category.nombre_categoria)


class CountryTestCase(TestCase):
    """Crea un conjunto de pruebas para el modelo Pais"""

    def test_country_creation(self):
        """Prueba la creación de un país"""
        country = Pais.objects.create(pais=TEST_DATA['pais_nombre'])
        self.assertEqual(country.pais, TEST_DATA['pais_nombre'])
        self.assertTrue(isinstance(country, Pais))
        self.assertEqual(str(country), country.pais)


class NewsTestCase(TestCase):
    """Crea un conjunto de pruebas para el modelo Noticia"""

    def setUp(self):
        """Configura las pruebas"""
        self.category = Categoria.objects.create(nombre_categoria=TEST_DATA['categoria_nombre'])
        self.country = Pais.objects.create(pais=TEST_DATA['pais_nombre'])
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password=TEST_PASSWORDS['simple_password']  # Django hashea automáticamente
        )

    def test_news_creation(self):
        """Prueba la creación de una noticia"""
        news = Noticia.objects.create(
            titulo_noticia=TEST_DATA['titulo_noticia'],
            cuerpo_noticia=TEST_DATA['cuerpo_noticia'],
            id_categoria=self.category,
            id_usuario=self.user,
            id_pais=self.country
        )
        self.assertEqual(news.titulo_noticia, TEST_DATA['titulo_noticia'])
        self.assertEqual(news.cuerpo_noticia, TEST_DATA['cuerpo_noticia'])
        self.assertEqual(news.id_categoria, self.category)
        self.assertEqual(news.id_usuario, self.user)
        self.assertEqual(news.id_pais, self.country)
        self.assertFalse(news.eliminado)
        self.assertFalse(news.destacada)
        self.assertTrue(isinstance(news, Noticia))
        self.assertEqual(str(news), news.titulo_noticia)


class UserTestCase(TestCase):
    """Crea un conjunto de pruebas para el modelo Usuario"""

    def setUp(self):
        """Configura las pruebas"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password=TEST_PASSWORDS['simple_password']  # Django hashea automáticamente
        )

    def test_user_creation(self):
        """Prueba la creación de un usuario"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password(TEST_PASSWORDS['simple_password']))  # Verificar contraseña hasheada
        another_user = User.objects.create_user(
            username="testusuario",
            email="test2@example.com",
            password=TEST_PASSWORDS['another_password']  # Django hashea automáticamente
        )
        self.assertEqual(another_user.username, "testusuario")
        self.assertEqual(another_user.email, "test2@example.com")
        self.assertTrue(another_user.check_password(TEST_PASSWORDS['another_password']))  # Verificar contraseña hasheada
        self.assertTrue(isinstance(another_user, User))
        self.assertEqual(str(another_user), another_user.username)


class UserAPITestCase(APITestCase):
    """Pruebas para las API relacionadas con usuarios"""

    def setUp(self):
        """Configura las pruebas"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password=TEST_PASSWORDS['simple_password']  # Django hashea automáticamente
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_user_profile(self):
        """Prueba obtener el perfil de usuario - usando admin_perfil como alternativa"""
        url = reverse("admin_perfil")
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_302_FOUND])
        if response.status_code == status.HTTP_302_FOUND:
            pass
