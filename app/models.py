from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

# ==================== ROLES ====================
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)  # 'admin', 'docente', 'estudiante'
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

# ==================== USUARIOS ====================
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    ru = db.Column(db.String(20), unique=True, nullable=False)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    def __repr__(self):
        return f"<Usuario: {self.nombre_completo}>"

# ==================== CURSOS ====================
class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    paralelo = db.Column(db.String(10), nullable=False)
    num_sesiones = db.Column(db.Integer, nullable=False, default=3)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    gestion = db.Column(db.Integer, nullable=False)  # Ej: 2026
    
    docente = db.relationship('Usuario', backref='cursos_impartidos')
    inscripciones = db.relationship('Inscripcion', backref='curso', lazy=True)
    sesiones = db.relationship('Sesion', backref='curso', lazy=True)

# ==================== INSCRIPCIONES ====================
class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    pago_verificado = db.Column(db.Boolean, default=False)
    
    usuario = db.relationship('Usuario', backref='inscripciones')
    asistente = db.relationship('Asistencia', backref='inscripcion', lazy=True)

# ==================== SESIONES ====================
class Sesion(db.Model):
    __tablename__ = 'sesiones'
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    numero = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Sesion {self.numero} - Curso {self.curso_id}>"

# ==================== ASISTENCIAS ====================
class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'))
    sesion_id = db.Column(db.Integer, db.ForeignKey('sesiones.id'))
    presente = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    sesion = db.relationship('Sesion', backref='asistencias')

# ==================== PAGOS ====================
class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    monto = db.Column(db.Float, nullable=False)
    comprobante = db.Column(db.String(200))  # Ruta del archivo
    verificado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== CERTIFICADOS ====================
class Certificado(db.Model):
    __tablename__ = 'certificados'
    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'))
    emitidos = db.Column(db.DateTime, default=datetime.utcnow)
    codigo_verificacion = db.Column(db.String(50), unique=True)
    
    inscripcion = db.relationship('Inscripcion', backref='certificado')