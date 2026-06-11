from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.auth import auth_bp
from app.extensions import db, bcrypt
from app.models import Usuario

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter(
            (Usuario.ru == username) | (Usuario.email == username)
        ).first()
        
        if usuario and bcrypt.check_password_hash(usuario.password, password):
            login_user(usuario)
            flash('¡Inicio de sesión exitoso!', 'success')
            
            # Redirección según rol
            if usuario.rol.nombre == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif usuario.rol.nombre == 'docente':
                return redirect(url_for('cursos.lista_cursos'))  # Docentes van a crear cursos
            else:
                return redirect(url_for('cursos.mis_cursos'))  # Estudiantes van a sus cursos
        else:
            flash('Credenciales incorrectas', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.models import Rol
    
    if request.method == 'POST':
        ru = request.form.get('ru')
        ci = request.form.get('ci')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        rol_nombre = request.form.get('rol', 'estudiante')
        
        rol = Rol.query.filter_by(nombre=rol_nombre).first()
        if not rol:
            rol = Rol.query.first()
        
        if Usuario.query.filter_by(ru=ru).first():
            flash('El RU ya está registrado', 'warning')
            return redirect(url_for('auth.register'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'warning')
            return redirect(url_for('auth.register'))
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        nuevo_usuario = Usuario(
            ru=ru,
            ci=ci,
            nombre_completo=nombre,
            email=email,
            password=hashed_pw,
            rol_id=rol.id
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Registro exitoso. Ahora inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar. Intenta de nuevo.', 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))