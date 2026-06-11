from flask import Flask
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
    
    # INICIALIZAR BASE DE DATOS AUTOMÁTICAMENTE
    with app.app_context():
        db.create_all()
        
        # Crear roles si no existen
        from app.models import Rol
        roles_data = ['admin', 'docente', 'estudiante']
        for nombre in roles_data:
            if not Rol.query.filter_by(nombre=nombre).first():
                db.session.add(Rol(nombre=nombre))
        
        # Crear usuario admin por defecto si no existe
        from app.models import Usuario
        admin_existente = Usuario.query.filter_by(ru='000001').first()
        if not admin_existente:
            password_admin = bcrypt.generate_password_hash('admin123').decode('utf-8')
            rol_admin = Rol.query.filter_by(nombre='admin').first()
            
            admin_default = Usuario(
                ru='000001',
                ci='000001',
                nombre_completo='Administrador',
                email='admin@uni.edu',
                password=password_admin,
                rol_id=rol_admin.id
            )
            db.session.add(admin_default)
        
        db.session.commit()
        print("✅ Base de datos inicializada")
    
    return app