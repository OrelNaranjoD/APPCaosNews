"""
Constantes para pruebas de CaosNews
"""

# Credenciales de usuarios de prueba
TEST_USER_CREDENTIALS = {
    'username': 'JuanPerez',
    'email': 'juanperez@duocuc.cl',
    'password': 'PassSegura123?',  # Esta contraseña será hasheada automáticamente por Django
    'first_name': 'Juan',
    'last_name': 'Perez',
}

# Credenciales de usuarios QA
QA_USER_CREDENTIALS = {
    'admin': {
        'username': 'qa_admin',
        'email': 'admin@qa.caosnews.com',
        'password': 'qaadmin123',  # Esta contraseña será hasheada automáticamente por Django
        'first_name': 'Admin',
        'last_name': 'QA',
        'role': 'administrador',
        'is_staff': True,
        'is_superuser': True,
        'groups': ['Administrador'],
        'permissions': ['all'],  # Acceso completo incluyendo panel Django
    },
    'periodista': {
        'username': 'qa_periodista',
        'email': 'periodista@qa.caosnews.com',
        'password': 'qaperiodista123',  # Esta contraseña será hasheada automáticamente por Django
        'first_name': 'Periodista',
        'last_name': 'QA',
        'role': 'periodista',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['Periodista'],
        'permissions': ['add_noticia', 'change_noticia', 'view_noticia'],  # Crea y edita sus propias noticias
    },
    'editor': {
        'username': 'qa_editor',
        'email': 'editor@qa.caosnews.com',
        'password': 'qaeditor123',  # Esta contraseña será hasheada automáticamente por Django
        'first_name': 'Editor',
        'last_name': 'QA',
        'role': 'editor',
        'is_staff': True,
        'is_superuser': False,
        'groups': ['Editor'],
        'permissions': ['add_noticia', 'change_noticia', 'view_noticia', 'delete_noticia'],  # Crea y edita cualquier noticia
    },
    'usuario': {
        'username': 'qa_usuario',
        'email': 'usuario@qa.caosnews.com',
        'password': 'qausuario123',  # Esta contraseña será hasheada automáticamente por Django
        'first_name': 'Usuario',
        'last_name': 'QA',
        'role': 'usuario',
        'is_staff': False,
        'is_superuser': False,
        'groups': ['Usuario'],
        'permissions': ['view_noticia'],  # Ve noticias autorizadas
    }
}

# Otras contraseñas de prueba
TEST_PASSWORDS = {
    'valid_password': 'PassSegura123',
    'invalid_password': 'wrongpassword',
    'simple_password': 'password123',
    'another_password': 'password456',
}

# Datos de prueba para modelos
TEST_DATA = {
    'categoria_nombre': 'Actualidad',
    'pais_nombre': 'Chile',
    'titulo_noticia': 'Muere Tommy Rey, el padre de la cumbia chilena',
    'cuerpo_noticia': 'El legendario cantante Tommy Rey, considerado el padre de la cumbia en Chile, ha muerto a sus 80 años. Su legado musical perdurará por siempre.',
    'fecha_publicacion': '2023-10-01T12:00:00Z',
    'imagen_nombre': 'tommy.jpg',
    'usuario_autor': 'juanperez',
}

# Datos de prueba para suscripciones (solo para QA)
SUBSCRIPTION_TEST_DATA = {
    'plan_qa_especial': {
        'nombre': 'Plan QA Especial',
        'descripcion': 'Plan especial para pruebas de QA con tiempo limitado',
        'caracteristicas': '''Acceso completo para testing ✔️
Todas las funcionalidades ✔️
Datos de prueba ✔️
Expira en 1 día ⚠️''',
        'precios': [
            {
                'periodo': 'qa_test',
                'duracion_dias': 2,  # Muy corto para pruebas
                'precio': 1000.00,   # Precio simbólico
            }
        ]
    },
    'suscripcion_proxima_a_vencer': {
        'plan': 'Plan QA Especial',
        'usuario': 'juanperez',
        'precio_periodo': 'qa_test',
        'dias_restantes': 1,  # Expira en 1 día para probar notificaciones
        'estado': 'A',  # Activa
    }
}
