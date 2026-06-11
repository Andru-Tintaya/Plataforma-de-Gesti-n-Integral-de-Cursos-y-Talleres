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
    
    # User Loader para Flask-Login
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
    
    # Ruta principal
    from app.cursos.routes import cursos_bp
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        if not hasattr(login_manager, 'anonymous_user'):
            from flask_login import current_user
            if current_user.is_authenticated:
                if current_user.rol.nombre == 'admin':
                    return redirect(url_for('admin_bp.dashboard'))
                return redirect(url_for('cursos_bp.mis_cursos'))
        from flask import render_template
        return render_template('base.html')
    
    return app