# inicializar.py
from app import create_app
from app.extensions import db
from app.models import Rol

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    
    # Crear roles por defecto
    roles = ['admin', 'docente', 'estudiante']
    for nombre in roles:
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    
    db.session.commit()
    print("✅ Base de datos inicializada correctamente")
    print("✅ Roles creados: admin, docente, estudiante")