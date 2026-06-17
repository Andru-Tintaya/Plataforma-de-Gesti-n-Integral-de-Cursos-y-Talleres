from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.extensions import db, bcrypt
from app.models import Usuario, Rol

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Filtramos por RU o Email
        usuario = Usuario.query.filter(
            (Usuario.ru == username) | (Usuario.email == username)
        ).first()
        
        if usuario and bcrypt.check_password_hash(usuario.password, password):
            login_user(usuario)
            flash('¡Inicio de sesión exitoso!', 'success')
            
            # Redirección segura según rol
            if usuario.rol.nombre == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('cursos.mis_cursos'))
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
        
        # Buscar el rol
        rol = Rol.query.filter_by(nombre=rol_nombre).first()
        
        # Si no existe el rol, crear el rol 'estudiante' por defecto
        if not rol:
            # Crear el rol si no existe
            rol = Rol(nombre=rol_nombre)
            db.session.add(rol)
            db.session.commit()
            # Volver a buscar
            rol = Rol.query.filter_by(nombre=rol_nombre).first()
        
        if not rol:
            flash('Error: No se pudo asignar el rol', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verificar si RU ya existe
        if Usuario.query.filter_by(ru=ru).first():
            flash('El RU ya está registrado', 'warning')
            return redirect(url_for('auth.register'))
        
        # Verificar si Email ya existe
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'warning')
            return redirect(url_for('auth.register'))
        
        # Crear usuario
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
@auth_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = current_user
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validar email único si lo cambió
        if email != usuario.email:
            if Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado por otro usuario', 'warning')
                return redirect(url_for('auth.editar_perfil'))
        
        usuario.nombre_completo = nombre
        usuario.email = email
        
        # Actualizar contraseña con validación mínima de 6 caracteres
        if password:
            if len(password) >= 6:
                usuario.password = bcrypt.generate_password_hash(password).decode('utf-8')
            else:
                flash('La contraseña debe tener al menos 6 caracteres', 'warning')
                return redirect(url_for('auth.editar_perfil'))
        
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.editar_perfil'))
    
    return render_template('auth/editar_perfil.html', usuario=usuario)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))