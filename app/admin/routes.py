from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.extensions import db
from app.models import Usuario, Curso, Inscripcion, Pago, Sesion, Asistencia, Rol

# ============ DASHBOARD ============
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    total_usuarios = Usuario.query.count()
    total_cursos = Curso.query.count()
    inscripciones_pendientes = Inscripcion.query.filter_by(pago_verificado=False).count()
    pagos_pendientes = Pago.query.filter_by(verificado=False).count()
    
    stats = {
        'usuarios': total_usuarios,
        'cursos': total_cursos,
        'inscripciones': inscripciones_pendientes,
        'pagos': pagos_pendientes
    }
    
    return render_template('admin/dashboard_admin.html', stats=stats)

# ============ VALIDAR PAGOS ============
@admin_bp.route('/validar-pagos', methods=['GET', 'POST'])
@login_required
def validar_pagos():
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    if request.method == 'POST':
        inscripcion_id = request.form.get('inscripcion_id')
        accion = request.form.get('accion')
        
        inscripcion = Inscripcion.query.get(inscripcion_id)
        
        if inscripcion:
            if accion == 'aprobar':
                inscripcion.pago_verificado = True
                flash(f'Pago aprobado', 'success')
            elif accion == 'rechazar':
                db.session.delete(inscripcion)
                flash(f'Inscripción eliminada', 'warning')
            
            db.session.commit()
            return redirect(url_for('admin.validar_pagos'))
    
    inscripciones = Inscripcion.query.filter_by(pago_verificado=False).all()
    
    return render_template('admin/validar_pagos.html', inscripciones=inscripciones)

# ============ REPORTES ============
@admin_bp.route('/reportes')
@login_required
def reportes():
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    cursos = Curso.query.all()
    reporte = []
    
    for curso in cursos:
        sesiones = Sesion.query.filter_by(curso_id=curso.id).all()
        inscripciones = Inscripcion.query.filter_by(
            curso_id=curso.id,
            pago_verificado=True
        ).count()
        
        total_asistencia = 0
        for sesion in sesiones:
            total_asistencia += Asistencia.query.filter_by(
                sesion_id=sesion.id,
                presente=True
            ).count()
        
        reporte.append({
            'curso': curso,
            'inscritos': inscripciones,
            'asistencias': total_asistencia
        })
    
    return render_template('admin/reportes.html', reporte=reporte)

# ============ LISTA USUARIOS ============
@admin_bp.route('/usuarios')
@login_required
def usuarios():
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    usuarios = Usuario.query.all()
    roles = Rol.query.all()
    
    return render_template('admin/usuarios.html', usuarios=usuarios, roles=roles)

# ============ EDITAR USUARIO ============
@admin_bp.route('/editar-usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()
    
    if request.method == 'POST':
        usuario.nombre_completo = request.form.get('nombre')
        usuario.email = request.form.get('email')
        usuario.rol_id = request.form.get('rol_id')
        
        # Cambiar contraseña si se proporciona
        nueva_pass = request.form.get('password')
        if nueva_pass:
            from app.extensions import bcrypt
            usuario.password = bcrypt.generate_password_hash(nueva_pass).decode('utf-8')
        
        db.session.commit()
        flash(f'Usuario {usuario.nombre_completo} actualizado', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', usuario=usuario, roles=roles)

# ============ ELIMINAR USUARIO ============
@admin_bp.route('/eliminar-usuario/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    usuario = Usuario.query.get_or_404(id)
    
    # No dejar que se elimine a sí mismo
    if usuario.id == current_user.id:
        flash('No puedes eliminarte a ti mismo', 'warning')
        return redirect(url_for('admin.usuarios'))
    
    nombre = usuario.nombre_completo
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuario {nombre} eliminado', 'success')
    return redirect(url_for('admin.usuarios'))

# ============ ELIMINAR CURSO ============
@admin_bp.route('/eliminar-curso/<int:id>', methods=['POST'])
@login_required
def eliminar_curso(id):
    if current_user.rol.nombre != 'admin':
        flash('Acceso restringido', 'danger')
        return redirect(url_for('cursos.mis_cursos'))
    
    curso = Curso.query.get_or_404(id)
    nombre = curso.nombre
    
    # Eliminar primero las inscripciones relacionadas
    Inscripcion.query.filter_by(curso_id=id).delete()
    Sesion.query.filter_by(curso_id=id).delete()
    
    db.session.delete(curso)
    db.session.commit()
    
    flash(f'Curso {nombre} eliminado', 'success')
    return redirect(url_for('admin.dashboard'))