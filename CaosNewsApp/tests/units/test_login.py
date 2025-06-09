"""
Tests unitarios para funcionalidad de login
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ValidationError as FormsValidationError
from unittest.mock import patch
import json

from CaosNewsApp.forms import LoginForm, RegisterForm

User = get_user_model()


class LoginFormTest(TestCase):
    """Tests para el formulario de login"""

    def test_login_form_valid_data(self):
        """Test que el formulario de login acepta datos válidos"""
        form_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_missing_email(self):
        """Test que el formulario requiere email"""
        form_data = {
            'password': 'TestPass123!'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_login_form_missing_password(self):
        """Test que el formulario requiere contraseña"""
        form_data = {
            'email': 'test@example.com'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_login_form_invalid_email(self):
        """Test que el formulario valida formato de email"""
        form_data = {
            'email': 'invalid-email',
            'password': 'TestPass123!'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class RegisterFormTest(TestCase):
    """Tests para el formulario de registro"""

    def test_register_form_valid_data(self):
        """Test que el formulario de registro acepta datos válidos"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

    def test_register_form_password_mismatch(self):
        """Test que las contraseñas deben coincidir"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'DifferentPass123!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Las contraseñas no coinciden', str(form.errors))

    def test_register_form_weak_password(self):
        """Test que rechaza contraseñas débiles"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'weakpass',  # Sin mayúsculas, números o símbolos
            'confirm_password': 'weakpass'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_register_form_password_too_short(self):
        """Test que rechaza contraseñas muy cortas"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'Aa1!',  # Solo 4 caracteres
            'confirm_password': 'Aa1!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_register_form_missing_uppercase(self):
        """Test que requiere al menos una mayúscula"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'securepass123!',  # Sin mayúsculas
            'confirm_password': 'securepass123!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_register_form_missing_symbol(self):
        """Test que requiere al menos un símbolo"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'SecurePass123',  # Sin símbolos
            'confirm_password': 'SecurePass123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class LoginViewTest(TestCase):
    """Tests para las vistas de login"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.login_url = reverse('login')

        # Crear usuario de prueba usando get_user_model()
        User = get_user_model()
        self.test_user = User.objects.create(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password=make_password('ValidPass123!')
        )

    def test_login_view_get(self):
        """Test que la vista de login responde correctamente a GET"""
        response = self.client.get('/')  # Página principal que contiene el modal
        self.assertEqual(response.status_code, 200)

    def test_login_success_with_email(self):
        """Test de login exitoso usando email"""
        login_data = {
            'identifier': 'test@example.com',
            'password': 'ValidPass123!'
        }
        response = self.client.post(self.login_url, login_data)

        # Verificar que el login fue exitoso
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta es JSON válida
        try:
            data = json.loads(response.content)
            self.assertTrue(data.get('valid', False))
        except json.JSONDecodeError:
            self.fail("La respuesta no es JSON válido")

    def test_login_success_with_username(self):
        """Test de login exitoso usando username"""
        login_data = {
            'identifier': 'testuser',
            'password': 'ValidPass123!'
        }
        response = self.client.post(self.login_url, login_data)

        # Verificar que el login fue exitoso
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta es JSON válida
        try:
            data = json.loads(response.content)
            self.assertTrue(data.get('valid', False))
        except json.JSONDecodeError:
            self.fail("La respuesta no es JSON válido")

    def test_login_failure_wrong_password(self):
        """Test de login fallido con contraseña incorrecta"""
        login_data = {
            'identifier': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data)

        # Verificar que el login falló
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta indica error
        try:
            data = json.loads(response.content)
            self.assertFalse(data.get('valid', True))
            self.assertIn('error_message', data)
        except json.JSONDecodeError:
            self.fail("La respuesta no es JSON válido")

    def test_login_failure_nonexistent_user(self):
        """Test de login fallido con usuario inexistente"""
        login_data = {
            'identifier': 'nonexistent@example.com',
            'password': 'ValidPass123!'
        }
        response = self.client.post(self.login_url, login_data)

        # Verificar que el login falló
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta indica error
        try:
            data = json.loads(response.content)
            self.assertFalse(data.get('valid', True))
            self.assertIn('error_message', data)
        except json.JSONDecodeError:
            self.fail("La respuesta no es JSON válido")

    def test_login_empty_credentials(self):
        """Test de login con credenciales vacías"""
        login_data = {
            'identifier': '',
            'password': ''
        }
        response = self.client.post(self.login_url, login_data)

        # Verificar que el login falló
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta indica error
        try:
            data = json.loads(response.content)
            self.assertFalse(data.get('valid', True))
        except json.JSONDecodeError:
            self.fail("La respuesta no es JSON válido")

    def test_login_csrf_protection(self):
        """Test que la vista de login tiene protección CSRF"""
        # Intentar login sin token CSRF
        self.client = Client(enforce_csrf_checks=True)
        login_data = {
            'identifier': 'test@example.com',
            'password': 'ValidPass123!'
        }
        response = self.client.post(self.login_url, login_data)

        # Debería fallar por falta de token CSRF
        self.assertEqual(response.status_code, 403)


class RegisterViewTest(TestCase):
    """Tests para las vistas de registro"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_success(self):
        """Test de registro exitoso"""
        register_data = {
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'username': 'nuevousuario',
            'email': 'nuevo@example.com',
            'password': 'SecureNewPass123!',
            'confirm_password': 'SecureNewPass123!'
        }
        response = self.client.post(self.register_url, register_data)

        # Verificar que el registro fue exitoso
        self.assertEqual(response.status_code, 200)

        # Verificar que el usuario fue creado
        User = get_user_model()
        self.assertTrue(User.objects.filter(email='nuevo@example.com').exists())

    def test_register_duplicate_email(self):
        """Test de registro con email duplicado"""
        # Crear usuario existente usando get_user_model()
        User = get_user_model()
        User.objects.create(
            username='existing',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password=make_password('ValidPass123!')
        )

        # Intentar registrar con el mismo email
        register_data = {
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'username': 'nuevousuario',
            'email': 'existing@example.com',  # Email duplicado
            'password': 'SecureNewPass123!',
            'confirm_password': 'SecureNewPass123!'
        }
        response = self.client.post(self.register_url, register_data)

        # Verificar que el registro falló
        self.assertEqual(response.status_code, 200)

        # Verificar que no se creó un segundo usuario con el mismo email
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)


class PasswordValidationIntegrationTest(TestCase):
    """Tests de integración para validación de contraseñas"""

    def test_password_validation_examples(self):
        """Test con ejemplos específicos de contraseñas"""
        test_cases = [
            # (password, should_be_valid, description)
            ('PassSegura123!', True, 'Contraseña válida con todos los requisitos'),
            ('passinsegura', False, 'Sin mayúsculas, números o símbolos'),
            ('PASSINSEGURA', False, 'Sin minúsculas, números o símbolos'),
            ('Pass123', False, 'Sin símbolos especiales'),
            ('PassSegura!', False, 'Sin números'),
            ('passsegura123!', False, 'Sin mayúsculas'),
            ('Pp1!', False, 'Muy corta (menos de 8 caracteres)'),
            ('MiContraseñaSegura123!', True, 'Contraseña larga y válida'),
            ('password', False, 'Contraseña muy común'),
            ('123456789', False, 'Solo números'),
        ]

        for password, should_be_valid, description in test_cases:
            with self.subTest(password=password, description=description):
                form_data = {
                    'first_name': 'Test',
                    'last_name': 'User',
                    'username': f'testuser_{password[:5]}',
                    'email': f'test_{password[:5]}@example.com',
                    'password': password,
                    'confirm_password': password
                }
                form = RegisterForm(data=form_data)

                if should_be_valid:
                    self.assertTrue(
                        form.is_valid(),
                        f"La contraseña '{password}' debería ser válida. Errores: {form.errors}"
                    )
                else:
                    self.assertFalse(
                        form.is_valid(),
                        f"La contraseña '{password}' debería ser inválida"
                    )


@pytest.mark.django_db
class TestLoginPytest:
    """Tests usando pytest para login"""

    def test_user_creation_with_secure_password(self):
        """Test que se puede crear usuario con contraseña segura"""
        User = get_user_model()
        user = User.objects.create_user(
            username='pytestuser',
            email='pytest@example.com',
            password='SecurePass123!',
            first_name='Pytest',
            last_name='User'
        )
        assert user.check_password('SecurePass123!')
        assert user.email == 'pytest@example.com'

    def test_authentication_backend(self):
        """Test del backend de autenticación personalizado"""
        from django.contrib.auth import authenticate

        # Crear usuario
        User = get_user_model()
        user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='AuthPass123!',
            first_name='Auth',
            last_name='User'
        )

        # Test autenticación por email
        authenticated_user = authenticate(username='auth@example.com', password='AuthPass123!')
        assert authenticated_user is not None
        assert authenticated_user.email == 'auth@example.com'

        # Test autenticación por username
        authenticated_user = authenticate(username='authuser', password='AuthPass123!')
        assert authenticated_user is not None
        assert authenticated_user.username == 'authuser'
