from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_migrate import Migrate
from app.extensions import db, bcrypt, login_manager
from app.config import Config

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))
    
    # Registrar Blueprints
    from app.auth import auth_bp
    from app.cursos import cursos_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cursos_bp, url_prefix='/cursos')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # RUTA RAÍZ - Redirigir según el rol
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # Asegurarse de que el rol exista antes de acceder a .nombre
            if current_user.rol:
                if current_user.rol.nombre == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('cursos.mis_cursos'))
        return redirect(url_for('auth.login'))
    
    # INICIALIZACIÓN DE BASE DE DATOS Y DATOS POR DEFECTO
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        from app.models import Rol, Usuario
        
        # 1. Crear Roles si no existen
        roles_data = ['admin', 'docente', 'estudiante']
        for nombre in roles_data:
            if not Rol.query.filter_by(nombre=nombre).first():
                db.session.add(Rol(nombre=nombre))
        
        # Guardar roles primero para asegurar las relaciones
        db.session.commit()
        
        # 2. Crear Administrador por defecto
        if not Usuario.query.filter_by(ru='000001').first():
            rol_admin = Rol.query.filter_by(nombre='admin').first()
            if rol_admin:
                password_admin = bcrypt.generate_password_hash('admin123').decode('utf-8')
                
                admin_default = Usuario(
                    ru='000001',
                    ci='000001',
                    nombre_completo='Administrador',
                    email='admin@uni.edu',
                    password=password_admin,
                    rol_id=rol_admin.id
                )
                db.session.add(admin_default)
                db.session.commit() # Commit final tras crear el admin
    
    return app