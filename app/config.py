import os

# Obtenemos la ruta absoluta de la carpeta donde vive config.py
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 1. Usar una clave secreta desde variables de entorno es mejor por seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asistencia-uni-2026'
    
    # 2. Ruta absoluta: Esto garantiza que SQLite cree el archivo en el lugar correcto
    # independientemente de dónde se ejecute el proceso.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'asistencia.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 3. Configuración extra necesaria para que Render y Flask se lleven bien con las cookies
    SESSION_COOKIE_SECURE = True   # Solo permite cookies en conexiones HTTPS
    SESSION_COOKIE_HTTPONLY = True # Impide acceso a cookies desde JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'