"""
Constantes para pruebas de CaosNews
"""

# Credenciales de usuarios de prueba
TEST_USER_CREDENTIALS = {
    'username': 'juanperez',
    'email': 'juanperez@duocuc.cl',
    'password': 'PassSegura123',  # Esta contraseña será hasheada automáticamente por Django
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
    'categoria_nombre': 'Prueba',
    'pais_nombre': 'Chile',
    'noticia_titulo': 'Título de prueba',
    'noticia_cuerpo': 'Cuerpo de la noticia de prueba',
}
