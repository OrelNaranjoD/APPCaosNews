from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from PIL import Image
import io

from CaosNewsApp.models import Noticia, Usuario, Categoria, Pais
from CaosNewsApp.forms import NoticiaForm

### Pruebas para CaosNews ###

# Pruebas para el modelo Noticia
class ModeloNoticiaTest(TestCase):
	def setUp(self):
		self.usuario = User.objects.create_user('usuario_prueba', 'usuario@prueba.com', 'password_prueba')
		self.categoria = Categoria.objects.create(nombre_categoria='Deportes')

	def test_creacion_noticia(self):
		noticia = Noticia.objects.create(titulo_noticia='Noticia de prueba', cuerpo_noticia='Contenido de prueba', id_categoria=self.categoria, id_usuario=self.usuario)
		self.assertEqual(noticia.titulo_noticia, 'Noticia de prueba')

# Pruebas para la vista de noticias
class VistaNoticiasTest(APITestCase):
	def test_vista_noticias(self):
		url = reverse('noticias', kwargs={'categoria': 'entretenimiento'})
		respuesta = self.client.get(url)
		self.assertEqual(respuesta.status_code, 200)

# Pruebas para el formulario de noticias
class FormularioNoticiaTest(TestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(username='usuario_prueba', password='contraseña', email='email@prueba.com')
		self.categoria = Categoria.objects.create(nombre_categoria='Categoria de prueba')
		self.pais = Pais.objects.create(pais='Pais de prueba')

	def test_formulario_valido(self):
		form_data = {
			'titulo_noticia': 'Noticia de prueba',
			'cuerpo_noticia': 'Contenido de prueba',
			'id_categoria': self.categoria.id_categoria,
			'id_pais': self.pais.id_pais,
			'id_usuario': self.usuario.id
		}
		form = NoticiaForm(data=form_data)
		self.assertTrue(form.is_valid())

# Pruebas para la vista de login
class VistaLoginTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='12345')

	def test_login_exitoso(self):
		self.client.login(username='testuser', password='12345')
		respuesta = self.client.get(reverse('home'))
		self.assertEqual(str(respuesta.context['user']), 'testuser')

# Pruebas para la creación de noticias con imagen
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import io
from CaosNewsApp.models import Categoria, Pais
class NoticiaTest(TestCase):
	def setUp(self):
		Categoria.objects.get_or_create(id_categoria=14, defaults={'nombre_categoria': 'Publicidad'})
		Pais.objects.get_or_create(id_pais=1, defaults={'pais': 'Chile'})
		self.user, _ = User.objects.get_or_create(username='CaosNews', defaults={'email': 'test@example.com', 'password': 'testpassword'})
		User.objects.get_or_create(id=5, defaults={'username': 'user5', 'email': 'user5@example.com', 'password': 'password5'})

	def test_creacion_publicidad(self):
		token = Token.objects.create(user=self.user)
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

		url = '/api/publicidad/'
		imagen = io.BytesIO()
		Image.new('RGB', (100, 100)).save(imagen, 'JPEG')
		imagen.name = 'test.jpg'
		imagen.seek(0)

		payload = {
			'titulo': 'Noticia de prueba',
			'cuerpo': 'Contenido de la noticia de prueba',
			'imagen': imagen,
		}

		respuesta = client.post(url, payload, format='multipart')
		self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
